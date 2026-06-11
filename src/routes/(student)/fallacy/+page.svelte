<script lang="ts">
	import { Brain, Award, Zap, History, Calendar, Trophy, TrendingUp, ChevronRight, FileText, Link2, Video, Mic } from 'lucide-svelte';
	import FallacyInput from '$lib/components/fallacy/FallacyInput.svelte';
	import FallacyEmpty from '$lib/components/fallacy/FallacyEmpty.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let stats = $derived(data.stats);
	let history = $derived(data.history);
	let dailyChallenge = $derived(data.dailyChallenge);

	let isLoading = $state(false);
	let progress = $state(0);
	let loadMsgIndex = $state(0);
	let loadingTimer: ReturnType<typeof setInterval> | null = null;

	const LOAD_MSGS = [
		'Membaca argumen…',
		'Memisahkan klaim dari kebisingan…',
		'Menelusuri nalar dan premis…',
		'Memeriksa silang klaim dengan Qdrant DB…',
		'Mengevaluasi kesimpulan di Llama-3-70B…',
		'Menyusun putusan akhir…'
	];

	$effect(() => {
		if (isLoading) {
			progress = 0;
			loadMsgIndex = 0;
			loadingTimer = setInterval(() => {
				progress += Math.random() * 8 + 4;
				if (progress >= 100) {
					progress = 100;
					loadMsgIndex = LOAD_MSGS.length - 1;
					if (loadingTimer) clearInterval(loadingTimer);
				} else {
					const idx = Math.min(
						LOAD_MSGS.length - 1,
						Math.floor((progress / 100) * LOAD_MSGS.length)
					);
					loadMsgIndex = idx;
				}
			}, 180);
		} else {
			if (loadingTimer) {
				clearInterval(loadingTimer);
				loadingTimer = null;
			}
			progress = 0;
			loadMsgIndex = 0;
		}

		return () => {
			if (loadingTimer) clearInterval(loadingTimer);
		};
	});

	// Challenge States passed to FallacyInput
	let challengeUrl = $state('');
	let challengeType = $state<'text' | 'url' | 'youtube' | 'audio'>('text');
	let challengeId = $state<string | null>(null);

	function startChallenge() {
		if (!dailyChallenge || dailyChallenge.completed) return;
		challengeUrl = dailyChallenge.content_url;
		challengeType = dailyChallenge.content_type as any;
		challengeId = dailyChallenge.id;
	}

	// Calculate XP percentage towards next level (100 XP per level)
	let xpProgress = $derived(stats ? stats.xp_points % 100 : 0);

	function getInputIcon(type: string) {
		if (type === 'url') return Link2;
		if (type === 'youtube') return Video;
		if (type === 'audio') return Mic;
		return FileText;
	}
</script>

<svelte:head>
	<title>Tribunal Logika · FallacyChecker · Revonalar</title>
	<meta name="description" content="Ajukan argumen dan terima vonis logikanya." />
</svelte:head>

<div class="relative overflow-x-hidden min-h-screen py-10">
	<!-- Background Glow -->
	<div class="pointer-events-none fixed inset-0 z-0">
		<div
			class="absolute -top-[340px] -left-[220px] h-[760px] w-[760px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,.15), rgba(218,43,34,0) 62%);"
		></div>
		<div
			class="absolute -right-[120px] -bottom-[220px] h-[520px] w-[520px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,0.08), rgba(218,43,34,0) 62%);"
		></div>
	</div>

	<div class="relative z-10 mx-auto max-w-[1240px] px-8">
		<!-- Header -->
		<header class="mb-12 border-b pb-8" style="border-color: var(--line);">
			<span class="kicker">TRIBUNAL LOGIKA · CASE MANAGEMENT</span>
			<h1 class="mt-4 text-[2.8rem] md:text-[3.8rem] leading-[1.02] font-black tracking-[-.045em] text-balance">
				Ajukan Argumen. <span class="serif text-red">Terima Vonisnya.</span>
			</h1>
			<p class="mt-4 max-w-[50ch] text-[1.1rem] text-ink-2 leading-relaxed">
				Gunakan akselerator AMD Instinct™ MI300X untuk membedah argumen tertulis, transkrip video, tautan berita, atau berkas audio dalam hitungan detik.
			</p>
		</header>

		{#if isLoading}
			<!-- Examining Loader overlay -->
			<div class="card p-12 text-center md:p-16 mb-10 max-w-[880px] mx-auto border-red/20" style="background: var(--surface);">
				<div class="mx-auto h-2 max-w-[520px] overflow-hidden rounded-lg bg-surface-2 border border-line">
					<div class="h-full rounded-lg transition-[width] duration-200" style="width: {progress}%; background: var(--red);"></div>
				</div>
				<div class="mt-4 font-mono text-[11px] tracking-[.16em] text-muted">{Math.round(progress)}% SELESAI</div>
				<div class="serif mt-8 min-h-[1.5em] text-[1.6rem] md:text-[2.1rem] text-ink italic font-semibold">
					"{LOAD_MSGS[loadMsgIndex]}"
				</div>
				<p class="mt-2 font-mono text-[10px] tracking-[.12em] text-muted uppercase">MENGEVALUASI ARTIKEL DAN TRANSKRIP DI AMD INSTINCT</p>
			</div>
		{:else}
			<div class="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] items-start">
				
				<!-- Left Column: Inputs & Challenges -->
				<div class="space-y-8">
					<!-- Daily Challenge -->
					{#if dailyChallenge}
						<div class="card overflow-hidden border-red/10" style="background: var(--surface);">
							<div class="p-6">
								<div class="flex flex-wrap items-center justify-between gap-3 border-b pb-3 mb-4" style="border-color: var(--line);">
									<div class="flex items-center gap-2">
										<Calendar class="h-4 w-4 text-red" />
										<span class="font-mono text-[12px] font-bold tracking-[.16em] text-red uppercase">TANTANGAN HARIAN</span>
									</div>
									<div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-green bg-green-soft px-2.5 py-0.5 rounded-full border border-green/10">
										<Award class="h-3.5 w-3.5" />
										+{dailyChallenge.diamond_reward} DIAMONDS
									</div>
								</div>

								<div class="flex items-start gap-4">
									<div class="hidden sm:grid h-12 w-12 place-items-center rounded-xl bg-surface-2 border border-line shrink-0 text-red">
										<Trophy class="h-6 w-6" />
									</div>
									<div>
										<h3 class="text-[19px] font-black text-ink leading-tight">Uji Logika Kasus Hari Ini</h3>
										<p class="mt-2 text-[14.5px] text-ink-2 leading-relaxed">
											Uji kemampuan berpikir kritis Anda dengan menganalisis argumen berikut. Cari:
											<span class="font-mono text-[12px] text-red font-bold uppercase ml-1">
												{dailyChallenge.expected_fallacy_types.join(', ')}
											</span>
										</p>
										
										{#if dailyChallenge.completed}
											<div class="mt-4 inline-flex items-center gap-2 font-mono text-[12px] text-green font-bold uppercase">
												✓ TANTANGAN HARI INI TELAH SELESAI
											</div>
										{:else}
											<button
												onclick={startChallenge}
												class="btn-primary mt-4 px-5 py-2.5 text-[13.5px] cursor-pointer"
											>
												Mulai Tantangan
											</button>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- Input Component -->
					<FallacyInput
						bind:isLoading
						initialType={challengeType}
						initialUrl={challengeUrl}
						challengeId={challengeId}
					/>
				</div>

				<!-- Right Column: Stats & History -->
				<div class="space-y-8">
					<!-- User Stats -->
					{#if stats}
						<div class="card p-6" style="background: var(--surface);">
							<div class="border-b pb-4 mb-4 flex items-center justify-between" style="border-color: var(--line);">
								<div class="flex items-center gap-2">
									<TrendingUp class="h-4 w-4 text-red" />
									<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">NALAR STATS</h3>
								</div>
								<span class="font-mono text-[12.5px] text-muted">LEVEL {stats.level}</span>
							</div>

							<!-- Level & XP progress -->
							<div class="mb-6">
								<div class="flex justify-between items-baseline mb-1.5 font-mono text-[13px]">
									<span class="font-bold text-ink">XP PROGRESSION</span>
									<span class="text-muted">{stats.xp_points % 100} / 100 XP</span>
								</div>
								<div class="h-2 w-full bg-surface-2 border border-line rounded-full overflow-hidden">
									<div class="h-full rounded-full" style="width: {xpProgress}%; background: var(--red);"></div>
								</div>
							</div>

							<!-- Mini Stats Grid -->
							<div class="grid grid-cols-2 gap-4">
								<div class="rounded-xl border p-4 bg-surface-2" style="border-color: var(--line);">
									<div class="font-mono text-[10px] text-muted tracking-wide uppercase">STREAK SAAT INI</div>
									<div class="text-[28px] font-black text-ink mt-1 flex items-baseline gap-1">
										{stats.current_streak}
										<span class="text-[12px] text-muted font-normal uppercase">Hari</span>
									</div>
									<div class="font-mono text-[9px] text-muted uppercase mt-1">MAX STREAK: {stats.longest_streak} HARI</div>
								</div>

								<div class="rounded-xl border p-4 bg-surface-2" style="border-color: var(--line);">
									<div class="font-mono text-[10px] text-muted tracking-wide uppercase">TOTAL PEMERIKSAAN</div>
									<div class="text-[28px] font-black text-ink mt-1 flex items-baseline gap-1">
										{stats.total_analyses}
										<span class="text-[12px] text-muted font-normal uppercase">Kasus</span>
									</div>
									<div class="font-mono text-[9px] text-muted uppercase mt-1">LOGIKA AMAN: {Math.round(stats.accuracy_score)}%</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- Recent History -->
					<div class="card p-6" style="background: var(--surface);">
						<div class="border-b pb-4 mb-4 flex items-center justify-between" style="border-color: var(--line);">
							<div class="flex items-center gap-2">
								<History class="h-4 w-4 text-red" />
								<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">RIWAYAT ANALISIS</h3>
							</div>
							<a href="/fallacy/history" class="font-mono text-[11px] text-red border-b border-red/20 hover:border-red">LIHAT ARSIP →</a>
						</div>

						{#if history.length === 0}
							<FallacyEmpty message="Anda belum pernah mengajukan pemeriksaan argumen." />
						{:else}
							<div class="divide-y" style="border-color: var(--line);">
								{#each history as item}
									{@const Icon = getInputIcon(item.input_type)}
									<a
										href="/fallacy/result/{item.id}"
										class="flex items-center justify-between py-3.5 group hover:px-2 hover:bg-surface-2 rounded-lg transition-all"
									>
										<div class="flex items-center gap-3 overflow-hidden pr-4">
											<div class="h-9 w-9 rounded-lg bg-surface-2 border border-line grid place-items-center text-ink shrink-0 group-hover:bg-ink group-hover:text-white transition-all">
												<Icon class="h-4.5 w-4.5" />
											</div>
											<div class="overflow-hidden">
												<h4 class="text-[14.5px] font-bold text-ink leading-tight truncate group-hover:text-red transition-all">
													{item.input_title || 'Untitled Argument'}
												</h4>
												<p class="font-mono text-[10px] text-muted uppercase mt-0.5">
													{new Date(item.created_at).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}
												</p>
											</div>
										</div>
										<div class="flex items-center gap-2 shrink-0">
											<span class="font-mono text-[12.5px] font-bold text-red">
												{item.total_count} {item.total_count > 1 ? 'Fallacies' : 'Fallacy'}
											</span>
											<ChevronRight class="h-4 w-4 text-muted group-hover:translate-x-1 transition-all" />
										</div>
									</a>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
