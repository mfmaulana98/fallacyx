<script lang="ts">
	import type { FallacyItem } from '$lib/types/fallacy';
	import FallacyBadge from './FallacyBadge.svelte';
	import { createEventDispatcher } from 'svelte';

	let {
		fallacies,
		mode = 'full',
		showIndex = true
	}: {
		fallacies: FallacyItem[];
		mode?: 'compact' | 'full';
		showIndex?: boolean;
	} = $props();

	const dispatch = createEventDispatcher<{
		fallacyFeedback: { fallacy_id: string; vote: 'correct' | 'incorrect' };
	}>();

	let votes = $state<Record<string, 'correct' | 'incorrect'>>({});

	function fallacyId(fallacy: FallacyItem, index: number): string {
		return fallacy.fallacy_id ?? String(index);
	}

	function vote(fallacy: FallacyItem, index: number, value: 'correct' | 'incorrect') {
		const id = fallacyId(fallacy, index);
		votes[id] = value;
		dispatch('fallacyFeedback', { fallacy_id: id, vote: value });
	}

	function severityFor(confidence: number): 'low' | 'medium' | 'high' {
		if (confidence >= 0.8) return 'high';
		if (confidence >= 0.5) return 'medium';
		return 'low';
	}
</script>

<ol class="divide-y divide-line">
	{#each fallacies as fallacy, index (fallacyId(fallacy, index))}
		{@const id = fallacyId(fallacy, index)}
		{@const currentVote = votes[id]}
		<li class="py-6 first:pt-0 last:pb-0">
			<div class="flex flex-wrap items-center gap-3">
				{#if showIndex}
					<span class="font-mono text-xs font-bold tracking-[0.16em] text-muted">
						{String(index + 1).padStart(2, '0')}
					</span>
				{/if}
				<FallacyBadge
					type={fallacy.type}
					severity={severityFor(fallacy.confidence)}
					confidence={fallacy.confidence}
					showConfidence={mode === 'full'}
				/>
			</div>

			<p
				class="serif mt-3 text-[15px] leading-relaxed text-ink-2"
				class:line-clamp-1={mode === 'compact'}
			>
				"{fallacy.text}"
			</p>

			{#if mode === 'full'}
				<p class="mt-2 text-[15px] leading-relaxed text-ink-2 font-sans">
					{fallacy.explanation}
				</p>
			{/if}

			<div class="mt-3 h-1.5 w-full max-w-50 overflow-hidden rounded-pill bg-surface-2 border border-line">
				<div
					class="h-full rounded-pill bg-red"
					style="width: 100%; opacity: {fallacy.confidence};"
				></div>
			</div>

			<div class="mt-3 flex justify-end gap-2">
				<button
					type="button"
					class="rounded-pill border border-line-2 px-2.5 py-1 text-xs transition-colors cursor-pointer"
					class:bg-green-soft={currentVote === 'correct'}
					class:border-green={currentVote === 'correct'}
					onclick={() => vote(fallacy, index, 'correct')}
					aria-label="Vonis ini benar"
				>
					👍
				</button>
				<button
					type="button"
					class="rounded-pill border border-line-2 px-2.5 py-1 text-xs transition-colors cursor-pointer"
					class:bg-red-soft={currentVote === 'incorrect'}
					class:border-red={currentVote === 'incorrect'}
					onclick={() => vote(fallacy, index, 'incorrect')}
					aria-label="Vonis ini salah"
				>
					👎
				</button>
			</div>
		</li>
	{/each}
</ol>
