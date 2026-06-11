<script lang="ts">
	const placeholders = [0, 1, 2];
</script>

<div class="pagein" aria-hidden="true" aria-busy="true">
	<div class="shimmer h-4 w-[60%] rounded-pill"></div>

	<ol class="mt-6 divide-y divide-line">
		{#each placeholders as i (i)}
			<li class="py-6 first:pt-0 last:pb-0">
				<div class="flex items-center gap-3">
					<div class="shimmer h-[30px] w-[30px] shrink-0 rounded-[9px]"></div>
					<div class="shimmer h-4 w-[40%] rounded-pill"></div>
				</div>

				<div class="mt-4 space-y-2">
					<div class="shimmer h-3.5 w-full rounded-pill"></div>
					<div class="shimmer h-3.5 w-[85%] rounded-pill"></div>
				</div>

				<div class="mt-4 h-1.5 w-full max-w-50 overflow-hidden rounded-pill bg-surface-2 border border-line">
					<div class="shimmer h-full w-full"></div>
				</div>
			</li>
		{/each}
	</ol>
</div>

<style>
	.shimmer {
		background: linear-gradient(90deg, #efede7 25%, #f5f4f0 50%, #efede7 75%);
		background-size: 200% 100%;
	}

	@media (prefers-reduced-motion: no-preference) {
		.shimmer {
			animation: shimmer 1.5s infinite;
		}
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}
</style>
