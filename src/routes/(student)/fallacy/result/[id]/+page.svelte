<script lang="ts">
	import { Scale, FileText, Link2, Video, Mic, Calendar, Cpu, Clock, ArrowLeft, Share2, ExternalLink } from 'lucide-svelte';
	import { browser } from '$app/environment';
	import FallacyCard from '$lib/components/fallacy/FallacyCard.svelte';
	import FallacyChart from '$lib/components/fallacy/FallacyChart.svelte';
	import FallacyTimeline from '$lib/components/fallacy/FallacyTimeline.svelte';
	import FallacyBadge from '$lib/components/fallacy/FallacyBadge.svelte';
	import type { PageData } from './$types';
	import type { Fallacy } from '$lib/types/fallacy';

	let { data }: { data: PageData } = $props();

	let analysis = $derived(data.analysis);
	let feedbackMap = $derived(data.feedbackMap);
	let fallacies = $derived((analysis.fallacies as unknown as Fallacy[]) || []);
	let MediumIcon = $derived(getInputIcon(analysis.input_type));

	let shareText = $state('Bagikan Kasus');

	function copyToClipboard() {
		if (browser) {
			navigator.clipboard.writeText(window.location.href);
			shareText = 'Tautan Disalin! ✓';
			setTimeout(() => {
				shareText = 'Bagikan Kasus';
			}, 2500);
		}
	}

	let severityLevel = $derived(
		analysis.total_count >= 3
			? 'BERAT'
			: analysis.total_count >= 1
				? 'SUBSTANSIAL'
				: 'AMAN'
	);

	function getInputIcon(type: string) {
		if (type === 'url') return Link2;
		if (type === 'youtube') return Video;
		if (type === 'audio') return Mic;
		return FileText;
	}

	function getMediumLabel(type: string) {
		if (type === 'url') return 'URL ARTIKEL';
		if (type === 'youtube') return 'YOUTUBE VIDEO';
		if (type === 'audio') return 'BERKAS AUDIO';
		return 'DOKUMEN TEKS';
	}

	// Dynamic lessons mapping based on detected fallacies
	let uniqueFallacyNames = $derived(
		Array.from(new Set(fallacies.map((f) => f.name).filter((n): n is string => !!n)))
	);
</script>

<svelte:head>
	<title>Verdict: {analysis.input_title || 'Kasus'} · FallacyChecker · Revonalar</title>
</svelte:head>

<div class="relative overflow-x-hidden min-h-screen py-10">
	<!-- Background Glow -->
	<div class="pointer-events-none fixed inset-0 z-0">
		<div
			class="absolute -top-[340px] -left-[220px] h-[760px] w-[760px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,.12), rgba(218,43,34,0) 62%);"
		></div>
	</div>

	<div class="relative z-10 mx-auto max-w-[1240px] px-8">
		<!-- Back to dashboard -->
		<div class="mb-8">
			<a
				href="/fallacy"
				class="inline-flex items-center gap-2 font-mono text-[12px] font-bold text-muted hover:text-red transition-colors uppercase"
			>
				<ArrowLeft class="h-4 w-4" />
				KEMBALI KE TRIBUNAL
			</a>
		</div>

		<!-- Page Title -->
		<header class="mb-10 border-b pb-6" style="border-color: var(--line);">
			<span class="kicker">TRIBUNAL LOGIKA · PUTUSAN KASUS</span>
			<h1 class="mt-4 text-[2.6rem] md:text-[3.2rem] leading-[1.05] font-black tracking-[-.04em]">
				Putusan Logika: <span class="serif text-red">{analysis.input_title || 'Kasus Tanpa Nama'}</span>
			</h1>
		</header>

		<!-- Main Verdict Card (Dark Section) -->
		<section class="dark-section p-8 md:p-12 mb-10">
			<div class="flex flex-wrap justify-between gap-4 border-b pb-6 font-mono text-[11px] tracking-[.18em] text-on-dark-mut uppercase" style="border-color: rgba(244,242,238,.12);">
				<span>KASUS NO. FX-{analysis.id.slice(0, 8).toUpperCase()}</span>
				<span class="flex items-center gap-1.5">
					<Calendar class="h-3.5 w-3.5" />
					DIPERIKSA: {new Date(analysis.created_at).toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })}
				</span>
			</div>

			<div class="mt-8 grid gap-8 md:grid-cols-[auto_auto_1fr] items-center">
				<div class="pr-6 md:border-r" style="border-color: rgba(244,242,238,.12);">
					<div class="text-[4.5rem] leading-[.8] font-black text-on-dark">{analysis.total_count}</div>
					<div class="mt-3.5 font-mono text-[10px] tracking-[.14em] text-on-dark-mut uppercase leading-none">Fallacies Ditemukan</div>
				</div>

				<div class="pr-6 md:border-r" style="border-color: rgba(244,242,238,.12);">
					<div class="text-[2.2rem] font-black text-red tracking-tight leading-none uppercase">{severityLevel}</div>
					<div class="mt-3.5 font-mono text-[10px] tracking-[.14em] text-on-dark-mut uppercase leading-none">Tingkat Keparahan</div>
				</div>

				<div class="serif text-[1.45rem] leading-[1.4] text-on-dark pl-0 md:pl-4">
					{#if analysis.total_count > 0}
						"Argumen ini didapati mengandung beberapa cacat penalaran yang melemahkan validitas kesimpulannya."
					{:else}
						"Luar biasa. Argumen ini bersih dari cacat logika umum. Kesimpulan ditopang dengan nalar yang sehat."
					{/if}
				</div>
			</div>

			<div class="mt-8 pt-6 border-t flex flex-wrap gap-x-8 gap-y-3 font-mono text-[11px] text-on-dark-mut uppercase" style="border-color: rgba(244,242,238,.12);">
				<span class="flex items-center gap-1.5">
					<Cpu class="h-3.5 w-3.5" />
					MODEL: {analysis.model_version || 'Llama-3-70B'}
				</span>
				<span class="flex items-center gap-1.5">
					<Clock class="h-3.5 w-3.5" />
					DURASI EVALUASI: {(analysis.metadata as any)?.duration_ms || 850} MS
				</span>
				<span class="flex items-center gap-1.5">
					<MediumIcon class="h-3.5 w-3.5" />
					MEDIUM: {getMediumLabel(analysis.input_type)}
				</span>
			</div>
		</section>

		<!-- Subsections: Timeline, Chart, and Fallacies -->
		<div class="grid gap-8 lg:grid-cols-[1.5fr_1fr] items-start">
			
			<!-- Left Column: Detailed fallacies list -->
			<div class="space-y-6">
				<div class="card p-6" style="background: var(--surface);">
					<div class="border-b pb-4 mb-4 flex items-center justify-between" style="border-color: var(--line);">
						<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">DAFTAR KEKELIRUAN NALAR</h3>
						<span class="font-mono text-[11px] text-muted">{analysis.total_count} KASUS KELIRU</span>
					</div>

					{#if fallacies.length === 0}
						<div class="py-12 text-center">
							<span class="badge-clear text-lg px-4 py-2">LOGIKA AMAN</span>
							<p class="mt-4 text-sm text-ink-2 max-w-sm mx-auto font-mono uppercase tracking-wide">
								Tidak ditemukan sesat pikir logika dalam analisis naskah ini.
							</p>
						</div>
					{:else}
						<div class="divide-y" style="border-color: var(--line);">
							{#each fallacies as fallacy, index}
								<div id="fallacy-card-{index}" class="transition-all duration-300">
									<FallacyCard
										{fallacy}
										{index}
										analysisId={analysis.id}
										initialFeedback={feedbackMap[index] || null}
									/>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Right Column: Visualizations & Extras -->
			<div class="space-y-6">
				<!-- Share and actions -->
				<div class="card p-6" style="background: var(--surface);">
					<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase border-b pb-4 mb-4" style="border-color: var(--line);">TINDAKAN KASUS</h3>
					<div class="flex flex-col gap-3">
						<button
							onclick={copyToClipboard}
							class="btn-secondary w-full justify-center cursor-pointer text-center text-sm py-3.5"
						>
							<Share2 class="h-4 w-4 mr-2" />
							{shareText}
						</button>
						<a
							href="/fallacy"
							class="btn-ghost w-full justify-center text-center text-sm py-3.5"
						>
							Periksa Argumen Lain
						</a>
					</div>
				</div>

				<!-- Timeline (if media contains timestamp) -->
				{#if analysis.input_type === 'youtube' || analysis.input_type === 'audio'}
					<FallacyTimeline {fallacies} />
				{/if}

				<!-- Distribution Chart -->
				<FallacyChart {fallacies} />

				<!-- Pelajari Lebih Lanjut -->
				{#if uniqueFallacyNames.length > 0}
					<div class="card p-6" style="background: var(--surface);">
						<div class="border-b pb-4 mb-4" style="border-color: var(--line);">
							<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">PELAJARI LEBIH LANJUT</h3>
						</div>
						<p class="text-sm text-ink-2 mb-4 leading-relaxed">
							Penasaran dengan struktur logika cacat pikir yang terdeteksi? Pelajari teorinya di kurikulum berpikir kritis Revonalar:
						</p>
						<ul class="space-y-3">
							{#each uniqueFallacyNames as name}
								<li>
									<a
										href="/curriculum/fallacy-{name.toLowerCase().replace(/\s+/g, '-')}"
										class="inline-flex items-center justify-between w-full p-3 rounded-xl border border-line bg-surface-2 hover:border-red hover:bg-white group transition-all"
									>
										<span class="font-mono text-[13px] font-bold text-ink uppercase tracking-wide group-hover:text-red transition-all">{name}</span>
										<span class="flex items-center gap-1 font-mono text-[10.5px] text-muted group-hover:text-red transition-all">
											PELAJARI
											<ExternalLink class="h-3 w-3" />
										</span>
									</a>
								</li>
							{/each}
						</ul>
					</div>
				{/if}
			</div>

		</div>
	</div>
</div>
