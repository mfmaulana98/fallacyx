import { error, json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';
import type { Fallacy } from '$lib/types/fallacy';

const MIN_LENGTH = 10;
const MAX_LENGTH = 10_000;

type BackendSeverity = 'low' | 'medium' | 'high';

interface BackendFallacyItem {
	fallacy_type: string;
	name_id: string;
	name_en: string;
	quote: string;
	explanation: string;
	confidence: number;
	severity: BackendSeverity;
	start_char: number | null;
	end_char: number | null;
}

interface BackendAnalysisResponse {
	id: string;
	input_type: 'text';
	mode: 'quick' | 'educational';
	language: 'id' | 'en';
	fallacies: BackendFallacyItem[];
	overall_assessment: string;
	is_clean: boolean;
	total_fallacies: number;
	model_used: string;
	analysis_duration_ms: number;
	created_at: string;
}

const SEVERITY_RANK: Record<BackendSeverity, number> = { low: 1, medium: 2, high: 3 };

/**
 * Proxies text submissions to the FastAPI inference backend on AMD Developer Cloud.
 * Keeps the backend URL and any future auth headers off the client.
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
	let body: { content?: string; mode?: 'quick' | 'educational'; language?: 'id' | 'en' };

	try {
		body = await request.json();
	} catch {
		throw error(400, 'Permohonan tidak valid. Sertakan teks argumen dalam format JSON.');
	}

	const text = (body.content ?? '').trim();

	if (text.length < MIN_LENGTH) {
		throw error(400, `Argumen terlalu pendek. Minimal ${MIN_LENGTH} karakter untuk diperiksa.`);
	}
	if (text.length > MAX_LENGTH) {
		throw error(400, `Argumen terlalu panjang. Maksimal ${MAX_LENGTH.toLocaleString('id-ID')} karakter.`);
	}

	const backendUrl = env.VITE_AMD_BACKEND_URL;
	if (!backendUrl) {
		throw error(500, 'Tribunal belum terhubung ke layanan pemeriksaan. Hubungi administrator.');
	}

	let backendResponse: Response;
	try {
		backendResponse = await fetch(`${backendUrl}/analyze/text`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				text,
				mode: body.mode ?? 'quick',
				language: body.language ?? 'id'
			})
		});
	} catch {
		throw error(503, 'Layanan pemeriksaan AMD sedang tidak dapat dijangkau. Coba lagi sesaat lagi.');
	}

	if (!backendResponse.ok) {
		let detail = 'Tribunal gagal memproses argumen ini.';
		try {
			const errBody = (await backendResponse.json()) as { detail?: string };
			if (errBody?.detail) detail = errBody.detail;
		} catch {
			// keep default detail
		}
		throw error(backendResponse.status, detail);
	}

	const data = (await backendResponse.json()) as BackendAnalysisResponse;

	const fallacies: Fallacy[] = data.fallacies.map((item) => ({
		type: item.fallacy_type,
		type_label: item.name_en,
		text: item.quote,
		explanation: item.explanation,
		confidence: item.confidence,
		timestamp_start: null,
		timestamp_end: null,
		name: item.name_en,
		excerpt: item.quote,
		explain: item.explanation
	}));

	const overall_severity = data.is_clean
		? 'clean'
		: data.fallacies.reduce<BackendSeverity>(
				(acc, f) => (SEVERITY_RANK[f.severity] > SEVERITY_RANK[acc] ? f.severity : acc),
				'low'
			);

	return json({
		id: data.id,
		fallacies,
		overall_assessment: data.overall_assessment,
		is_clean: data.is_clean,
		total_count: data.total_fallacies,
		overall_severity,
		model_version: data.model_used,
		processing_time_ms: data.analysis_duration_ms,
		created_at: data.created_at
	});
};
