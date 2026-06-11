<script lang="ts">
	import { getFallacyByCode } from '$lib/data/fallacies';

	type Severity = 'low' | 'medium' | 'high';

	let {
		type,
		severity,
		confidence,
		showConfidence = false
	}: {
		type: string;
		severity: Severity;
		confidence: number;
		showConfidence?: boolean;
	} = $props();

	const SEVERITY_STYLES: Record<Severity, { bg: string; border: string; text: string }> = {
		low: { bg: 'rgba(217, 119, 6, 0.1)', border: 'rgba(217, 119, 6, 0.3)', text: '#B45309' },
		medium: { bg: 'rgba(234, 88, 12, 0.1)', border: 'rgba(234, 88, 12, 0.32)', text: '#C2410C' },
		high: { bg: 'var(--red-soft)', border: 'rgba(218, 43, 34, 0.35)', text: 'var(--red)' }
	};

	const fallacy = $derived(getFallacyByCode(type));
	const label = $derived(fallacy?.name_en ?? type.replace(/_/g, ' '));
	const style = $derived(SEVERITY_STYLES[severity]);
</script>

<span
	class="inline-flex items-center gap-2 rounded-sm border px-2.5 py-1"
	class:pulse={severity === 'high'}
	style="background: {style.bg}; border-color: {style.border}; color: {style.text};"
>
	<span class="font-mono text-[10px] font-bold uppercase tracking-[0.18em]">{type}</span>
	<span class="font-sans text-[12.5px] font-semibold tracking-tight" style="color: var(--ink);">
		{label}
	</span>
	{#if showConfidence}
		<span class="font-mono text-[10px] font-bold uppercase tracking-[0.18em] opacity-80">
			{confidence.toFixed(2)}
		</span>
	{/if}
</span>
