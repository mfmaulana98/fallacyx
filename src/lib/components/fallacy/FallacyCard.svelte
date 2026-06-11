<script lang="ts">
	import type { Fallacy } from '$lib/types/fallacy';
	import { ThumbsUp, ThumbsDown, X, Clock } from 'lucide-svelte';
	import { enhance } from '$app/forms';

	let {
		fallacy,
		index,
		analysisId,
		initialFeedback = null
	}: {
		fallacy: Fallacy;
		index: number;
		analysisId: string;
		initialFeedback?: 'correct' | 'incorrect' | null;
	} = $props();

	let currentFeedback = $state<'correct' | 'incorrect' | null>(initialFeedback);
	let isSubmitting = $state(false);

	function setFeedback(value: 'correct' | 'incorrect') {
		currentFeedback = value;
	}
</script>

<article class="border-b py-7 last:border-b-0" style="border-color: var(--line);">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<div class="flex items-center gap-3.5">
			<span class="badge-fallacy rounded-[9px]! px-0! py-0! grid h-[30px] w-[30px] place-items-center font-extrabold bg-red-soft text-red">
				<X class="h-4 w-4" />
			</span>
			<h3 class="text-[22px] font-black tracking-tight md:text-[25px]">
				{String(index + 1).padStart(2, '0')} · {fallacy.name}
			</h3>
			{#if fallacy.timestamp}
				<span class="inline-flex items-center gap-1 font-mono text-[12px] text-muted bg-surface-2 px-2.5 py-1 rounded-md border border-line">
					<Clock class="h-3 w-3" />
					{fallacy.timestamp}
				</span>
			{/if}
		</div>
		<div class="text-right">
			<div class="font-mono text-[12px] font-bold text-red tracking-wider uppercase">CONFIDENCE {fallacy.confidence.toFixed(2)}</div>
			<div class="mt-1.5 h-1.5 w-[120px] overflow-hidden rounded-full bg-surface-2 border border-line">
				<div class="h-full rounded-full" style="width: {Math.round(fallacy.confidence * 100)}%; background: var(--red);"></div>
			</div>
		</div>
	</div>

	<span class="kicker muted mt-5 mb-1.5 block">KUTIPAN PEMICU</span>
	<p class="serif rounded-r-xl border-l-[3px] px-5 py-3.5 text-[16.5px] leading-relaxed" style="background: var(--surface-2); border-color: var(--red);">
		"{fallacy.excerpt}"
	</p>

	<span class="kicker muted mt-5 mb-1.5 block">KENAPA INI KELIRU</span>
	<p class="text-ink-2 text-[16px] leading-relaxed mb-4">{fallacy.explain}</p>

	<div class="rounded-[14px] p-4 bg-red-soft border border-red/10">
		<span class="kicker mb-0 block text-red">ARGUMEN YANG LEBIH KUAT AKAN</span>
		<p class="mt-1 text-ink text-[16px] leading-relaxed">{fallacy.fix}</p>
	</div>

	<!-- Feedback Actions -->
	<div class="mt-5 flex items-center justify-between gap-4 border-t pt-4 border-dashed border-line">
		<span class="font-mono text-[11px] text-muted uppercase tracking-wider">Apakah vonis ini akurat?</span>
		<div class="flex items-center gap-2">
			<form
				method="POST"
				action="?/submitFeedback"
				use:enhance={() => {
					isSubmitting = true;
					return async ({ update }) => {
						await update({ reset: false });
						isSubmitting = false;
					};
				}}
			>
				<input type="hidden" name="fallacyIndex" value={index} />
				<input type="hidden" name="isCorrect" value="true" />
				<button
					type="submit"
					onclick={() => setFeedback('correct')}
					disabled={isSubmitting}
					class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[12px] font-mono tracking-wider uppercase border transition-all cursor-pointer"
					style={currentFeedback === 'correct'
						? 'background: var(--green); border-color: var(--green); color: white;'
						: 'background: transparent; border-color: var(--line-2); color: var(--ink-2);'}
				>
					<ThumbsUp class="h-3.5 w-3.5" />
					BENAR
				</button>
			</form>

			<form
				method="POST"
				action="?/submitFeedback"
				use:enhance={() => {
					isSubmitting = true;
					return async ({ update }) => {
						await update({ reset: false });
						isSubmitting = false;
					};
				}}
			>
				<input type="hidden" name="fallacyIndex" value={index} />
				<input type="hidden" name="isCorrect" value="false" />
				<button
					type="submit"
					onclick={() => setFeedback('incorrect')}
					disabled={isSubmitting}
					class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[12px] font-mono tracking-wider uppercase border transition-all cursor-pointer"
					style={currentFeedback === 'incorrect'
						? 'background: var(--red); border-color: var(--red); color: white;'
						: 'background: transparent; border-color: var(--line-2); color: var(--ink-2);'}
				>
					<ThumbsDown class="h-3.5 w-3.5" />
					SALAH
				</button>
			</form>
		</div>
	</div>
</article>
