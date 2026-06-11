<script lang="ts">
	import { X } from 'lucide-svelte';

	type ErrorType = 'timeout' | 'unavailable' | 'invalid_input' | 'rate_limit' | 'unknown';

	let {
		errorType,
		message,
		onRetry
	}: {
		errorType: ErrorType;
		message: string;
		onRetry: () => void;
	} = $props();

	const headlines: Record<ErrorType, string> = {
		timeout: 'Tribunal sedang sibuk. Argumenmu antri untuk diperiksa.',
		unavailable: 'Mesin pemeriksa sedang offline. Coba beberapa menit lagi.',
		invalid_input: 'Argumen tidak terbaca. Pastikan teks minimal 10 karakter.',
		rate_limit: 'Kamu sudah mencapai batas 5 analisis hari ini. Upgrade untuk lebih.',
		unknown: 'Terjadi kesalahan tak terduga. Kami sedang memperbaikinya.'
	};

	let headline = $derived(headlines[errorType]);
</script>

<div class="flex items-start gap-4 rounded-r-[14px] border-l-4 border-red bg-surface-2 p-5 md:p-6" role="alert">
	<div class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-red-soft text-red">
		<X class="h-5 w-5" />
	</div>
	<div class="min-w-0 flex-1">
		<span class="kicker muted mb-1.5 block">PEMERIKSAAN GAGAL</span>
		<p class="text-[16px] leading-relaxed font-semibold text-ink">{headline}</p>
		{#if message}
			<p class="mt-1.5 font-mono text-[12px] tracking-tight text-muted">{message}</p>
		{/if}
		<button
			type="button"
			onclick={onRetry}
			class="mt-3 cursor-pointer text-[13px] font-bold text-red underline underline-offset-4 transition-opacity hover:opacity-70"
		>
			Coba lagi →
		</button>
	</div>
</div>
