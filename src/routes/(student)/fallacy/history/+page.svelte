<script lang="ts">
	import { Search, Filter, Calendar, ArrowLeft, ArrowRight, FileText, Link2, Video, Mic, RefreshCw, ChevronRight } from 'lucide-svelte';
	import FallacyEmpty from '$lib/components/fallacy/FallacyEmpty.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let analyses = $derived(data.analyses);
	let totalCount = $derived(data.totalCount);
	let page = $derived(data.page);
	let limit = $derived(data.limit);
	let filters = $derived(data.filters);

	let totalPages = $derived(Math.ceil(totalCount / limit) || 1);

	// Curated fallacy list for filter dropdown
	const fallaciesList = [
		'Ad Hominem',
		'False Dichotomy',
		'Appeal to Authority',
		'Straw Man',
		'Slippery Slope',
		'Ad Populum'
	];

	function getInputIcon(type: string) {
		if (type === 'url') return Link2;
		if (type === 'youtube') return Video;
		if (type === 'audio') return Mic;
		return FileText;
	}

	function getMediumLabel(type: string) {
		if (type === 'url') return 'Artikel';
		if (type === 'youtube') return 'YouTube';
		if (type === 'audio') return 'Audio';
		return 'Teks';
	}
</script>

<svelte:head>
	<title>Arsip Kasus · FallacyChecker · Revonalar</title>
</svelte:head>

<div class="relative overflow-x-hidden min-h-screen py-10">
	<!-- Background Glow -->
	<div class="pointer-events-none fixed inset-0 z-0">
		<div
			class="absolute -top-[340px] -left-[220px] h-[760px] w-[760px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,.10), rgba(218,43,34,0) 62%);"
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
			<span class="kicker">TRIBUNAL LOGIKA · ARSIP KASUS</span>
			<h1 class="mt-4 text-[2.6rem] md:text-[3.2rem] leading-[1.05] font-black tracking-[-.045em] text-balance">
				Arsip Kasus &amp; <span class="serif text-red">Riwayat Vonis</span>
			</h1>
		</header>

		<!-- Filters Panel -->
		<section class="card p-6 mb-8 bg-surface">
			<form method="GET" action="/fallacy/history" class="space-y-4">
				<input type="hidden" name="page" value="1" />
				<input type="hidden" name="limit" value={limit} />

				<!-- Grid: Search & Filters -->
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 items-end">
					
					<!-- Search Field -->
					<div class="space-y-1.5 col-span-1 sm:col-span-2 lg:col-span-1">
						<label for="search" class="kicker muted text-[11px] block">CARI KATA KUNCI</label>
						<div class="relative">
							<Search class="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
							<input
								id="search"
								type="text"
								name="search"
								value={filters.search}
								placeholder="Cari judul atau isi..."
								class="input pl-10"
							/>
						</div>
					</div>

					<!-- Medium Type -->
					<div class="space-y-1.5">
						<label for="inputType" class="kicker muted text-[11px] block">MEDIUM INPUT</label>
						<select id="inputType" name="inputType" class="input">
							<option value="all" selected={filters.inputType === 'all'}>Semua Medium</option>
							<option value="text" selected={filters.inputType === 'text'}>Teks Pidato/Utas</option>
							<option value="url" selected={filters.inputType === 'url'}>URL Artikel Berita</option>
							<option value="youtube" selected={filters.inputType === 'youtube'}>Tautan YouTube</option>
							<option value="audio" selected={filters.inputType === 'audio'}>Berkas Rekaman Audio</option>
						</select>
					</div>

					<!-- Fallacy Type -->
					<div class="space-y-1.5">
						<label for="fallacyType" class="kicker muted text-[11px] block">JENIS SESAT PIKIR</label>
						<select id="fallacyType" name="fallacyType" class="input">
							<option value="all" selected={filters.fallacyType === 'all'}>Semua Cacat Logika</option>
							{#each fallaciesList as type}
								<option value={type} selected={filters.fallacyType === type}>{type}</option>
							{/each}
						</select>
					</div>

					<!-- Start Date -->
					<div class="space-y-1.5">
						<label for="startDate" class="kicker muted text-[11px] block">DARI TANGGAL</label>
						<input
							id="startDate"
							type="date"
							name="startDate"
							value={filters.startDate}
							class="input"
						/>
					</div>

					<!-- End Date -->
					<div class="space-y-1.5">
						<label for="endDate" class="kicker muted text-[11px] block">SAMPAI TANGGAL</label>
						<input
							id="endDate"
							type="date"
							name="endDate"
							value={filters.endDate}
							class="input"
						/>
					</div>

					<!-- Submit & Clear Buttons -->
					<div class="flex gap-2.5 col-span-1 sm:col-span-2 lg:col-span-2">
						<button
							type="submit"
							class="btn-primary flex-1 justify-center cursor-pointer text-sm py-3"
						>
							<Filter class="h-4 w-4 mr-2" />
							Terapkan Filter
						</button>
						<a
							href="/fallacy/history"
							class="btn-ghost justify-center px-4 cursor-pointer"
							title="Reset Filters"
						>
							<RefreshCw class="h-4 w-4" />
						</a>
					</div>

				</div>
			</form>
		</section>

		<!-- List of Cases -->
		<section class="card p-6 bg-surface">
			<div class="border-b pb-4 mb-4 flex items-center justify-between" style="border-color: var(--line);">
				<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">BERKAS TRIBUNAL KASUS ({totalCount})</h3>
				<span class="font-mono text-[11px] text-muted uppercase">HALAMAN {page} DARI {totalPages}</span>
			</div>

			{#if analyses.length === 0}
				<FallacyEmpty message="Tidak ada arsip analisis yang cocok dengan filter Anda." />
			{:else}
				<div class="divide-y" style="border-color: var(--line);">
					{#each analyses as item}
						{@const Icon = getInputIcon(item.input_type)}
						<a
							href="/fallacy/result/{item.id}"
							class="flex flex-wrap items-center justify-between gap-4 py-4 group hover:px-3 hover:bg-surface-2 rounded-xl transition-all"
						>
							<div class="flex items-center gap-4 min-w-0 flex-1">
								<div class="h-11 w-11 rounded-xl bg-surface-2 border border-line grid place-items-center text-ink shrink-0 group-hover:bg-ink group-hover:text-white transition-all">
									<Icon class="h-5 w-5" />
								</div>
								<div class="min-w-0">
									<h4 class="text-[17px] font-black text-ink leading-tight truncate group-hover:text-red transition-all">
										{item.input_title || 'Untitled Case'}
									</h4>
									<div class="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10.5px] text-muted uppercase mt-1">
										<span>MEDIUM: {getMediumLabel(item.input_type)}</span>
										<span>FILED: {new Date(item.created_at).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
									</div>
								</div>
							</div>
							<div class="flex items-center gap-3 shrink-0">
								<span class="font-mono text-[13.5px] font-extrabold text-red bg-red-soft px-3 py-1 rounded-full border border-red/10">
									{item.total_count} {item.total_count > 1 ? 'FALLACIES' : 'FALLACY'}
								</span>
								<ChevronRight class="h-5 w-5 text-muted group-hover:translate-x-1.5 transition-all" />
							</div>
						</a>
					{/each}
				</div>

				<!-- Pagination Bar -->
				{#if totalPages > 1}
					<div class="flex items-center justify-between border-t pt-6 mt-6" style="border-color: var(--line);">
						<!-- Prev Button -->
						{#if page > 1}
							<a
								href="/fallacy/history?page={page - 1}&limit={limit}&search={filters.search}&inputType={filters.inputType}&fallacyType={filters.fallacyType}&startDate={filters.startDate}&endDate={filters.endDate}"
								class="btn-ghost py-2.5 px-4 cursor-pointer text-xs"
							>
								<ArrowLeft class="h-4 w-4 mr-1.5" />
								SEBELUMNYA
							</a>
						{:else}
							<button
								disabled
								class="btn-ghost py-2.5 px-4 opacity-40 cursor-not-allowed text-xs"
							>
								<ArrowLeft class="h-4 w-4 mr-1.5" />
								SEBELUMNYA
							</button>
						{/if}

						<span class="font-mono text-[12px] text-ink-2 uppercase">Halaman {page} / {totalPages}</span>

						<!-- Next Button -->
						{#if page < totalPages}
							<a
								href="/fallacy/history?page={page + 1}&limit={limit}&search={filters.search}&inputType={filters.inputType}&fallacyType={filters.fallacyType}&startDate={filters.startDate}&endDate={filters.endDate}"
								class="btn-ghost py-2.5 px-4 cursor-pointer text-xs"
							>
								SELANJUTNYA
								<ArrowRight class="h-4 w-4 ml-1.5" />
							</a>
						{:else}
							<button
								disabled
								class="btn-ghost py-2.5 px-4 opacity-40 cursor-not-allowed text-xs"
							>
								SELANJUTNYA
								<ArrowRight class="h-4 w-4 ml-1.5" />
							</button>
						{/if}
					</div>
				{/if}
			{/if}
		</section>
	</div>
</div>
