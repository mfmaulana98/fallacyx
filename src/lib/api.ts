import { createClient } from '$lib/supabase/client';
import type { Analysis } from '$lib/types/fallacy';

export type AnalysisResult = Analysis;

/** Mirrors the `errorType` union consumed by AnalysisError.svelte */
export type ApiErrorType = 'timeout' | 'unavailable' | 'invalid_input' | 'rate_limit' | 'unknown';

export class ApiError extends Error {
	errorType: ApiErrorType;
	status?: number;

	constructor(errorType: ApiErrorType, message: string, status?: number) {
		super(message);
		this.name = 'ApiError';
		this.errorType = errorType;
		this.status = status;
	}
}

const BASE_URL = import.meta.env.VITE_AMD_BACKEND_URL as string;

const RETRY_COUNT = 2;
const RETRY_DELAY_MS = 1000;

const TIMEOUT_SHORT_MS = 30_000; // text / url
const TIMEOUT_LONG_MS = 120_000; // youtube / audio

function sleep(ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Normalizes a non-OK fetch response into a typed ApiError and throws it. */
export async function handleApiError(response: Response): Promise<never> {
	let detail: string | undefined;
	try {
		const body = (await response.json()) as Record<string, unknown>;
		detail = (body?.detail ?? body?.message ?? body?.error) as string | undefined;
	} catch {
		// response body wasn't JSON — fall back to statusText
	}

	const message = detail ?? response.statusText ?? `Request failed with status ${response.status}`;

	switch (response.status) {
		case 400:
		case 422:
			throw new ApiError('invalid_input', message, response.status);
		case 408:
			throw new ApiError('timeout', message, response.status);
		case 429:
			throw new ApiError('rate_limit', message, response.status);
		case 503:
			throw new ApiError('unavailable', message, response.status);
		default:
			throw new ApiError('unknown', message, response.status);
	}
}

async function getAuthHeader(): Promise<Record<string, string>> {
	const supabase = createClient();
	const {
		data: { session }
	} = await supabase.auth.getSession();

	return session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
}

/** Fetch wrapper with auth header injection, timeout, and 503 retry logic. */
async function request(path: string, init: RequestInit, timeoutMs: number): Promise<Response> {
	const authHeader = await getAuthHeader();
	const headers = { ...authHeader, ...init.headers };

	for (let attempt = 0; attempt <= RETRY_COUNT; attempt++) {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

		try {
			const response = await fetch(`${BASE_URL}${path}`, {
				...init,
				headers,
				signal: controller.signal
			});

			if (response.status === 503 && attempt < RETRY_COUNT) {
				await sleep(RETRY_DELAY_MS);
				continue;
			}

			return response;
		} catch (err) {
			if (err instanceof DOMException && err.name === 'AbortError') {
				throw new ApiError('timeout', 'Permintaan melebihi batas waktu.');
			}
			throw new ApiError('unknown', err instanceof Error ? err.message : 'Gagal menghubungi server.');
		} finally {
			clearTimeout(timeoutId);
		}
	}

	throw new ApiError('unavailable', 'Server tidak tersedia setelah beberapa percobaan.');
}

export async function analyzeText(
	text: string,
	mode: 'quick' | 'educational' = 'quick'
): Promise<AnalysisResult> {
	const response = await request(
		'/api/analyze/text',
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ text, mode })
		},
		TIMEOUT_SHORT_MS
	);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function analyzeUrl(url: string): Promise<AnalysisResult> {
	const response = await request(
		'/api/analyze/url',
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url })
		},
		TIMEOUT_SHORT_MS
	);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function analyzeYoutube(youtubeUrl: string): Promise<AnalysisResult> {
	const response = await request(
		'/api/analyze/youtube',
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url: youtubeUrl })
		},
		TIMEOUT_LONG_MS
	);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function analyzeAudio(file: File): Promise<AnalysisResult> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await request(
		'/api/analyze/audio',
		{
			method: 'POST',
			body: formData
		},
		TIMEOUT_LONG_MS
	);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function getAnalysisById(id: string): Promise<AnalysisResult> {
	const response = await request(
		`/api/analysis/${encodeURIComponent(id)}`,
		{ method: 'GET' },
		TIMEOUT_SHORT_MS
	);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function getUserHistory(userId: string, page = 1): Promise<AnalysisResult[]> {
	const params = new URLSearchParams({ user_id: userId, page: String(page) });
	const response = await request(`/api/history?${params}`, { method: 'GET' }, TIMEOUT_SHORT_MS);

	if (!response.ok) await handleApiError(response);
	return response.json();
}

export async function submitFeedback(
	analysisId: string,
	fallacyIndex: number,
	vote: 'correct' | 'incorrect'
): Promise<void> {
	const response = await request(
		'/api/feedback',
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ analysis_id: analysisId, fallacy_index: fallacyIndex, vote })
		},
		TIMEOUT_SHORT_MS
	);

	if (!response.ok) await handleApiError(response);
}
