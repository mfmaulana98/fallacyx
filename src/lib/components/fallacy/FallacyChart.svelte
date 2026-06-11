<script lang="ts">
	import type { Fallacy } from '$lib/types/fallacy';

	let { fallacies = [] }: { fallacies: Fallacy[] } = $props();

	let fallacyCounts = $derived(
		fallacies.reduce(
			(acc, curr) => {
				const key = curr.type_label ?? curr.name;
				acc[key] = (acc[key] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>
		)
	);

	let chartData = $derived(
		Object.entries(fallacyCounts)
			.map(([label, count]) => ({
				label,
				count,
				percentage: (count / fallacies.length) * 100
			}))
			.sort((a, b) => b.count - a.count)
	);
</script>

<div class="card p-6 my-6">
	<div class="border-b pb-4 mb-5 flex justify-between items-center" style="border-color: var(--line);">
		<h4 class="font-mono text-[12px] tracking-[.24em] text-red uppercase">DISTRIBUSI KEKELIRUAN</h4>
		<span class="font-mono text-[11px] text-muted uppercase">{fallacies.length} FALLACIES TOTAL</span>
	</div>

	{#if chartData.length === 0}
		<div class="py-8 text-center text-muted font-mono text-[13px] uppercase">
			Tidak ada data visualisasi
		</div>
	{:else}
		<div class="space-y-5">
			{#each chartData as item (item.label)}
				<div>
					<div class="flex justify-between items-baseline mb-1.5 font-mono text-[13px]">
						<span class="font-bold text-ink">{item.label}</span>
						<span class="text-muted">{item.count} vonis ({Math.round(item.percentage)}%)</span>
					</div>
					<div class="h-3.5 w-full bg-surface-2 border border-line rounded-full overflow-hidden">
						<div
							class="h-full rounded-full transition-all duration-500 ease-out"
							style="width: {item.percentage}%; background: var(--red); box-shadow: 0 0 10px rgba(218, 43, 34, 0.2);"
						></div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
