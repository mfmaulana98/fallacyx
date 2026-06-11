<script lang="ts">
	import type { Fallacy } from '$lib/types/fallacy';
	import { Clock } from 'lucide-svelte';

	let {
		fallacies = []
	}: {
		fallacies: Fallacy[];
	} = $props();

	let timelineItems = $derived(
		fallacies
			.map((f, i) => ({ ...f, originalIndex: i }))
			.filter((f) => f.timestamp)
			.sort((a, b) => {
				return (a.timestamp || '').localeCompare(b.timestamp || '');
			})
	);

	function scrollToCard(index: number) {
		const el = document.getElementById(`fallacy-card-${index}`);
		if (el) {
			el.scrollIntoView({ behavior: 'smooth', block: 'center' });
			el.classList.add('bg-red-soft');
			setTimeout(() => el.classList.remove('bg-red-soft'), 1200);
		}
	}
</script>

<div class="card p-6 my-6">
	<div class="border-b pb-4 mb-5" style="border-color: var(--line);">
		<h4 class="font-mono text-[12px] tracking-[.24em] text-red uppercase">KRONOLOGI ARGUMEN · TIMELINE</h4>
	</div>

	{#if timelineItems.length === 0}
		<div class="py-8 text-center text-muted font-mono text-[13px] uppercase">
			Tidak ada data timestamp media
		</div>
	{:else}
		<div class="relative pl-6 border-l border-dashed" style="border-color: var(--line-2);">
			{#each timelineItems as item}
				<div class="relative mb-6 last:mb-0">
					<!-- Bullet point node on the line -->
					<div
						class="absolute -left-[31px] top-1.5 h-2 w-2 rounded-full bg-red"
						style="box-shadow: 0 0 8px var(--red);"
					></div>

					<div class="flex items-start gap-4">
						<button
							type="button"
							onclick={() => scrollToCard(item.originalIndex)}
							class="flex items-center gap-1.5 font-mono text-[12px] font-bold text-red bg-red-soft px-2.5 py-1 rounded-md border border-red/10 cursor-pointer hover:bg-red hover:text-white transition-all"
						>
							<Clock class="h-3 w-3" />
							{item.timestamp}
						</button>
						<div>
							<h5 class="text-[15px] font-extrabold text-ink leading-tight mb-1">
								{item.name}
							</h5>
							<p class="serif text-[13.5px] text-ink-2 italic line-clamp-1">
								"{item.excerpt}"
							</p>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
