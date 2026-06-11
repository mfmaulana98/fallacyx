<script lang="ts">
	import { Inbox } from 'lucide-svelte';
	let { message = 'Belum ada data analisis yang ditemukan.' }: { message?: string } = $props();
</script>

<div class="card flex flex-col items-center justify-center p-12 text-center my-6">
	<div class="grid h-16 w-16 place-items-center rounded-2xl text-muted bg-surface-2 mb-4 border border-line">
		<Inbox class="h-8 w-8" />
	</div>
	<h3 class="text-[20px] font-black tracking-tight text-ink mb-1.5">ARSIP KOSONG</h3>
	<p class="text-[14px] text-ink-2 max-w-xs font-mono tracking-tight uppercase leading-relaxed">{message}</p>
</div>
