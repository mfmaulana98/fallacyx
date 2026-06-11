<script lang="ts">
	import { writable, derived, get } from 'svelte/store';

	let {
		jobId,
		onComplete,
		onError
	}: {
		jobId: string;
		onComplete: (resultId: string) => void;
		onError: (message: string) => void;
	} = $props();

	type ProgressStatus = 'idle' | 'processing' | 'done' | 'error';

	interface ProgressEventPayload {
		step: string;
		progress?: number;
		message?: string;
		result_id?: string;
	}

	const status = writable<ProgressStatus>('idle');
	const percent = writable(0);
	const step = writable('');
	const message = writable('');

	const stepLabel = derived([status, step], ([$status, $step]) => {
		if ($status === 'done') return 'VERDICT READY';
		if ($status === 'error') return 'EXAMINATION FAILED';
		return $step.replace(/_/g, ' ').toUpperCase();
	});

	const barColor = derived(status, ($status) => {
		if ($status === 'done') return 'var(--green)';
		if ($status === 'error') return 'var(--red-deep)';
		return 'var(--red)';
	});

	const BASE_URL = import.meta.env.VITE_AMD_BACKEND_URL as string;
	const FADE_DELAY_MS = 900;
	const FADE_DURATION_MS = 400;

	let fadingOut = $state(false);

	let source: EventSource | null = null;
	let doneTimer: ReturnType<typeof setTimeout> | null = null;
	let fadeTimer: ReturnType<typeof setTimeout> | null = null;

	function clearTimers() {
		if (doneTimer) clearTimeout(doneTimer);
		if (fadeTimer) clearTimeout(fadeTimer);
		doneTimer = null;
		fadeTimer = null;
	}

	function closeConnection() {
		source?.close();
		source = null;
	}

	function handlePayload(payload: ProgressEventPayload) {
		if (typeof payload.progress === 'number') {
			percent.set(Math.max(0, Math.min(100, payload.progress)));
		}
		if (payload.message) message.set(payload.message);
		step.set(payload.step ?? '');

		if (payload.step === 'done') {
			percent.set(100);
			status.set('done');
			closeConnection();
			onComplete(payload.result_id ?? '');

			doneTimer = setTimeout(() => {
				fadingOut = true;
				fadeTimer = setTimeout(() => {
					status.set('idle');
					fadingOut = false;
				}, FADE_DURATION_MS);
			}, FADE_DELAY_MS);
		} else if (payload.step === 'error') {
			status.set('error');
			closeConnection();
			onError(payload.message ?? 'The examination could not be completed.');
		} else {
			status.set('processing');
		}
	}

	function connect() {
		clearTimers();
		fadingOut = false;
		percent.set(0);
		step.set('');
		message.set('');
		status.set('processing');

		source = new EventSource(`${BASE_URL}/progress/${jobId}`);

		source.onmessage = (event) => {
			try {
				handlePayload(JSON.parse(event.data));
			} catch {
				// malformed payload — ignore and wait for the next event
			}
		};

		source.onerror = () => {
			if (get(status) === 'processing') {
				const msg = 'Connection to the examination service was lost.';
				message.set(msg);
				status.set('error');
				onError(msg);
				closeConnection();
			}
		};
	}

	$effect(() => {
		connect();

		return () => {
			closeConnection();
			clearTimers();
		};
	});
</script>

{#if $status !== 'idle'}
	<div class="w-full transition-opacity ease-out" class:opacity-0={fadingOut} style="transition-duration: {FADE_DURATION_MS}ms">
		<div class="mb-2 flex items-baseline justify-between gap-3">
			<span class="font-mono text-[11px] font-bold tracking-[0.2em] text-ink uppercase">
				{$stepLabel}
			</span>
			<span class="font-mono text-xs font-bold tabular-nums" style="color: {$barColor}">
				{Math.round($percent)}%
			</span>
		</div>

		<div class="h-2 w-full overflow-hidden rounded-pill border border-line bg-surface-2">
			<div
				class="h-full rounded-pill transition-[width] duration-300 ease-out"
				style="width: {$percent}%; background: {$barColor};"
			></div>
		</div>

		{#if $message}
			<p
				class="mt-2.5 font-sans text-[0.92rem] italic"
				style="color: {$status === 'error' ? 'var(--red-deep)' : 'var(--ink-2)'}"
			>
				{$message}
			</p>
		{/if}
	</div>
{/if}
