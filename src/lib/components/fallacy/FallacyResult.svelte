<script lang="ts">
	import {
		ThumbsUp,
		ThumbsDown,
		Share2,
		Download,
		RefreshCw,
		ChevronDown,
		ChevronUp,
		Clock,
		ExternalLink,
		CheckCircle2,
		FileText,
		Link2,
		Video,
		Mic,
		AlertTriangle
	} from 'lucide-svelte';
	import { base } from '$app/paths';
	import { enhance } from '$app/forms';
	import { fade, slide } from 'svelte/transition';

	// ─── Types ────────────────────────────────────────────────────────────────

	interface FallacyItem {
		type: string;
		type_label: string;
		text: string;
		explanation: string;
		confidence: number;
		timestamp_start: number | null;
		timestamp_end: number | null;
	}

	interface Analysis {
		id: string;
		input_type: 'text' | 'url' | 'youtube' | 'audio';
		input_title: string | null;
		fallacies: FallacyItem[];
		total_count: number;
		processing_time_ms: number;
		transcript: string | null;
		created_at: string;
	}

	// ─── Props ────────────────────────────────────────────────────────────────

	let {
		analysis,
		isOwner = false,
		youtubeVideoId = null
	}: {
		analysis: Analysis;
		isOwner?: boolean;
		youtubeVideoId?: string | null;
	} = $props();

	// ─── Local State ──────────────────────────────────────────────────────────

	let transcriptOpen = $state(false);
	let feedbackMap = $state<Record<number, 'correct' | 'incorrect' | null>>({});
	let feedbackSubmitting = $state<Record<number, boolean>>({});
	let shareSuccess = $state(false);

	// ─── Derived Data ─────────────────────────────────────────────────────────

	// Count fallacies per type for the summary chart
	const fallacyCounts = $derived(
		analysis.fallacies.reduce(
			(acc, f) => {
				acc[f.type_label] = (acc[f.type_label] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>
		)
	);

	const chartData = $derived(
		Object.entries(fallacyCounts)
			.map(([label, count]) => ({ label, count }))
			.sort((a, b) => b.count - a.count)
	);

	// Highlight fallacy-containing text spans in transcript
	const transcriptHighlighted = $derived(() => {
		if (!analysis.transcript) return '';
		let t = analysis.transcript;
		// Escape HTML
		t = t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
		// Wrap each fallacy excerpt in a highlight span
		for (const f of analysis.fallacies) {
			const escaped = f.text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
			if (escaped && t.includes(escaped)) {
				t = t.replace(
					escaped,
					`<mark class="bg-red/10 border-b-2 border-red/40 text-red font-medium italic select-all cursor-help px-1 rounded-sm" title="${f.type_label}">${escaped}</mark>`
				);
			}
		}
		return t;
	});

	// ─── Helpers ─────────────────────────────────────────────────────────────

	const INPUT_TYPE_LABEL: Record<string, string> = {
		text: 'Teks',
		url: 'Artikel URL',
		youtube: 'YouTube',
		audio: 'Audio'
	};

	function formatDuration(ms: number): string {
		if (ms < 1000) return `${ms}ms`;
		return `${(ms / 1000).toFixed(1)} detik`;
	}

	function formatTimestamp(seconds: number): string {
		const m = Math.floor(seconds / 60);
		const s = Math.floor(seconds % 60);
		return `${m}:${String(s).padStart(2, '0')}`;
	}

	function confidenceLabel(c: number): { label: string; cls: string } {
		if (c >= 0.8) return { label: 'Tinggi', cls: 'bg-red-soft text-red' };
		if (c >= 0.5) return { label: 'Sedang', cls: 'bg-amber-500/10 text-amber-600 border border-amber-500/20' };
		return { label: 'Rendah', cls: 'bg-surface-2 text-ink-2 border border-line' };
	}

	// Deterministic palette by index so each type gets its own color
	const TYPE_COLORS = [
		'#DA2B22', // var(--red)
		'#7C3AED', // Purple
		'#0EA5E9', // Sky blue
		'#D97706', // Amber
		'#059669', // Green
		'#DB2777', // Pink
		'#EA580C'  // Orange
	] as const;

	function typeColor(index: number): string {
		return TYPE_COLORS[index % TYPE_COLORS.length];
	}

	const typeColorMap = $derived(
		chartData.reduce(
			(acc, item, i) => {
				acc[item.label] = typeColor(i);
				return acc;
			},
			{} as Record<string, string>
		)
	);

	async function handleShare() {
		const url = window.location.href;
		if (navigator.share) {
			try {
				await navigator.share({ title: 'Hasil Analisis Fallacy', url });
			} catch {
				// user cancelled share
			}
		} else {
			await navigator.clipboard.writeText(url);
			shareSuccess = true;
			setTimeout(() => (shareSuccess = false), 2000);
		}
	}

	function handleDownloadPdf() {
		window.print();
	}

	function getFallacyColor(fallacyLabel: string): string {
		return typeColorMap[fallacyLabel] ?? '#DA2B22';
	}

	function jumpToTimestamp(seconds: number) {
		if (!youtubeVideoId) return;
		const iframe = document.querySelector<HTMLIFrameElement>('#yt-embed-player');
		if (iframe?.contentWindow) {
			iframe.contentWindow.postMessage(
				JSON.stringify({ event: 'command', func: 'seekTo', args: [seconds, true] }),
				'*'
			);
			iframe.scrollIntoView({ behavior: 'smooth', block: 'center' });
		}
	}
</script>

<!-- Root container using Tailwind -->
<div class="w-full font-sans select-none antialiased">

	<!-- ══════════════════════════════════════════════════════════
	     1. HEADER SUMMARY (Verdict Banner)
	     ══════════════════════════════════════════════════════════ -->
	<div class="relative overflow-hidden rounded-[26px] bg-dark text-on-dark shadow-card-lg p-7 md:p-9">
		<!-- Background Glow -->
		<div class="absolute inset-0 pointer-events-none z-0">
			<div class="absolute -top-48 -right-48 w-96 h-96 rounded-full bg-radial from-red/20 to-transparent pointer-events-none"></div>
		</div>

		<div class="relative z-10">
			<!-- Top metadata row -->
			<div class="flex flex-wrap justify-between items-center gap-2 pb-4 border-b border-white/10">
				<span class="font-mono text-[11px] tracking-[.14em] uppercase text-on-dark-mut">
					RVN · TRIBUNAL · {analysis.id.slice(0, 8).toUpperCase()}
				</span>
				<span class="font-mono text-[11px] tracking-[.14em] uppercase text-on-dark-mut">
					{new Date(analysis.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}
				</span>
			</div>

			<!-- Main verdict stats -->
			<div class="grid grid-cols-1 md:grid-cols-[auto_1px_1fr] items-center gap-6 mt-6">
				<div class="flex flex-col">
					<span class="text-5xl md:text-6xl font-black text-white leading-none">
						{analysis.total_count}
					</span>
					<span class="font-mono text-[10px] tracking-[.14em] uppercase text-on-dark-mut mt-2.5">
						fallac{analysis.total_count === 1 ? 'y' : 'ies'} ditemukan
					</span>
				</div>

				<!-- Vertical separator -->
				<div class="hidden md:block h-14 w-[1px] bg-white/10"></div>

				<div>
					{#if analysis.input_title}
						<p class="font-serif italic text-xl md:text-2xl font-semibold text-white leading-snug mb-3">
							"{analysis.input_title}"
						</p>
					{/if}
					<div class="flex flex-wrap items-center gap-3">
						<!-- Input type badge -->
						<span class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-mono text-[11px] font-bold tracking-[0.14em] uppercase bg-red text-white">
							{#if analysis.input_type === 'text'}
								<FileText class="h-3 w-3" />
							{:else if analysis.input_type === 'url'}
								<Link2 class="h-3 w-3" />
							{:else if analysis.input_type === 'youtube'}
								<Video class="h-3 w-3" />
							{:else}
								<Mic class="h-3 w-3" />
							{/if}
							{INPUT_TYPE_LABEL[analysis.input_type]}
						</span>

						<!-- Duration stat -->
						<span class="font-mono text-[11px] tracking-wider uppercase text-on-dark-mut">
							Dianalisis dalam {formatDuration(analysis.processing_time_ms)}
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- ══════════════════════════════════════════════════════════
	     YouTube embed (if applicable)
	     ══════════════════════════════════════════════════════════ -->
	{#if youtubeVideoId && analysis.input_type === 'youtube'}
		<div class="card p-6 mt-6 bg-surface border border-line rounded-card shadow-card print:hidden">
			<div class="border-b border-line pb-4 mb-4">
				<span class="font-mono text-xs tracking-widest text-red font-bold uppercase">PLAYER VIDEO</span>
			</div>
			<div class="relative w-full pb-[56.25%] h-0 overflow-hidden rounded-xl">
				<iframe
					id="yt-embed-player"
					src="https://www.youtube.com/embed/{youtubeVideoId}?enablejsapi=1"
					title="YouTube video player"
					frameborder="0"
					allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
					allowfullscreen
					class="absolute inset-0 w-full h-full border-none"
				></iframe>
			</div>
		</div>
	{/if}

	<!-- ══════════════════════════════════════════════════════════
	     2. TIDAK ADA FALLACY
	     ══════════════════════════════════════════════════════════ -->
	{#if analysis.total_count === 0}
		<div class="card flex flex-col items-center justify-center p-12 text-center mt-6 bg-surface border border-line rounded-card shadow-card" in:fade={{ duration: 300 }}>
			<!-- Clean Icon -->
			<div class="h-20 w-20 rounded-full bg-green-soft border-2 border-dashed border-green/30 flex items-center justify-center mb-6">
				<svg class="h-10 w-10 text-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3" aria-hidden="true">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h3 class="text-2xl font-black text-ink tracking-tight mb-2">
				Tidak ditemukan <span class="font-serif italic text-green font-semibold">logical fallacy!</span>
			</h3>
			<p class="text-ink-2 max-w-md mb-6 leading-relaxed">
				Argumen ini tampak valid secara logika. Tidak ada pola kekeliruan yang terdeteksi.
			</p>
			<div class="inline-flex items-start gap-3 bg-surface-2 border border-line rounded-2xl p-4 text-left max-w-lg text-[11px] font-mono uppercase tracking-wide text-muted leading-relaxed">
				<AlertTriangle class="h-4 w-4 shrink-0 text-muted mt-0.5" />
				<span>Bukan berarti konten ini sepenuhnya benar — argumennya valid, namun kebenaran faktualnya belum diverifikasi.</span>
			</div>
		</div>

	<!-- ══════════════════════════════════════════════════════════
	     3. SUMMARY CHART  +  4. LIST FALLACY
	     ══════════════════════════════════════════════════════════ -->
	{:else}
		<!-- 3. Summary Chart -->
		<div class="card p-6 md:p-8 mt-6 bg-surface border border-line rounded-card shadow-card" in:fade={{ duration: 300 }}>
			<div class="border-b border-line pb-4 mb-6 flex flex-wrap justify-between items-center gap-2">
				<span class="font-mono text-xs tracking-widest text-red font-bold uppercase">DISTRIBUSI KEKELIRUAN</span>
				<span class="font-mono text-[11px] text-muted uppercase">{analysis.total_count} vonis total</span>
			</div>

			<!-- Pill badges per type -->
			<div class="flex flex-wrap gap-2 mb-6">
				{#each chartData as item, i (item.label)}
					<span
						class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-mono font-bold tracking-wide uppercase border transition-all hover:-translate-y-[1px]"
						style="background-color: color-mix(in srgb, {typeColor(i)} 10%, transparent); color: {typeColor(i)}; border-color: color-mix(in srgb, {typeColor(i)} 25%, transparent);"
					>
						{item.label} <span class="opacity-75">({item.count})</span>
					</span>
				{/each}
			</div>

			<!-- Bar chart -->
			<div class="space-y-4">
				{#each chartData as item, i (item.label)}
					<div class="grid grid-cols-[140px_1fr_40px] md:grid-cols-[180px_1fr_40px] items-center gap-4">
						<span class="text-xs md:text-sm font-bold text-ink truncate">{item.label}</span>
						<div class="h-3 bg-surface-2 border border-line rounded-full overflow-hidden">
							<div
								class="h-full rounded-full transition-all duration-700 ease-out"
								style="width: {(item.count / analysis.total_count) * 100}%; background-color: {typeColor(i)};"
							></div>
						</div>
						<span class="text-right font-mono text-xs text-muted">{item.count}</span>
					</div>
				{/each}
			</div>
		</div>

		<!-- 4. Fallacy List -->
		<div class="card p-6 md:p-8 mt-6 bg-surface border border-line rounded-card shadow-card" in:fade={{ duration: 300, delay: 80 }}>
			<div class="border-b border-line pb-4 mb-6">
				<span class="font-mono text-xs tracking-widest text-red font-bold uppercase">DAFTAR KEKELIRUAN</span>
			</div>

			<div class="divide-y divide-line">
				{#each analysis.fallacies as fallacy, idx (fallacy.type + "-" + idx)}
					{@const conf = confidenceLabel(fallacy.confidence)}
					{@const color = getFallacyColor(fallacy.type_label)}
					{@const fb = feedbackMap[idx] ?? null}
					{@const submitting = feedbackSubmitting[idx] ?? false}
					{@const severityClass = fallacy.confidence >= 0.8 ? 'badge-fallacy' : fallacy.confidence >= 0.5 ? 'badge-fallacy' : 'badge-caution'}

					<article class="py-8 first:pt-0 last:pb-0" id="fallacy-item-{idx}">
						<!-- Finding Header -->
						<div class="flex flex-wrap items-start justify-between gap-4">
							<div class="flex items-center flex-wrap gap-3">
								<!-- Index indicator -->
								<span
									class="h-8 w-8 rounded-lg border flex items-center justify-center font-mono font-bold text-xs"
									style="background-color: {color}12; color: {color}; border-color: {color}30;"
								>
									{String(idx + 1).padStart(2, '0')}
								</span>
								<h3 class="text-lg md:text-xl font-black text-ink tracking-tight">{fallacy.type_label}</h3>

								<!-- Timestamp link (for video/audio) -->
								{#if fallacy.timestamp_start !== null}
									<button
										type="button"
										class="inline-flex items-center gap-1 font-mono text-[11px] font-bold text-red bg-red-soft hover:bg-red hover:text-white border border-red/10 rounded-md px-2.5 py-1 transition-all cursor-pointer print:bg-transparent print:text-red"
										onclick={() => jumpToTimestamp(fallacy.timestamp_start!)}
										title="Lompat ke momen ini"
									>
										<Clock class="h-3 w-3" />
										{formatTimestamp(fallacy.timestamp_start)}
										{#if fallacy.timestamp_end !== null}
											→ {formatTimestamp(fallacy.timestamp_end)}
										{/if}
										{#if youtubeVideoId}
											<ExternalLink class="h-3 w-3 ml-0.5 print:hidden" />
										{/if}
									</button>
								{/if}
							</div>

							<!-- Confidence score -->
							<div class="flex items-center gap-3">
								<span class="inline-flex items-center rounded-full px-2.5 py-0.5 font-mono text-[10px] font-bold tracking-wider uppercase {conf.cls}">
									{conf.label}
								</span>
								<div class="h-1.5 w-20 bg-surface-2 border border-line rounded-full overflow-hidden hidden md:block">
									<div
										class="h-full rounded-full"
										style="width: {Math.round(fallacy.confidence * 100)}%; background-color: {color};"
									></div>
								</div>
								<span class="font-mono text-xs text-muted">{(fallacy.confidence * 100).toFixed(0)}%</span>
							</div>
						</div>

						<!-- Quote excerpt -->
						<span class="font-mono text-[10px] tracking-widest text-muted font-bold uppercase mt-6 mb-2 block">KUTIPAN PEMICU</span>
						<blockquote
							class="font-serif italic font-semibold text-[15px] md:text-[16px] leading-relaxed rounded-r-xl border-l-[3px] px-5 py-4 bg-surface-2"
							style="border-color: {color};"
						>
							"{fallacy.text}"
						</blockquote>

						<!-- Explanation -->
						<span class="font-mono text-[10px] tracking-widest text-muted font-bold uppercase mt-6 mb-2 block">KENAPA INI KELIRU</span>
						<p class="text-ink-2 text-[15px] leading-relaxed">{fallacy.explanation}</p>

						<!-- Feedback actions (only if isOwner) -->
						{#if isOwner}
							<div class="mt-6 border-t border-dashed border-line pt-4 flex flex-wrap items-center justify-between gap-4 print:hidden">
								<span class="font-mono text-[10px] text-muted uppercase tracking-wider">Apakah vonis ini akurat?</span>
								<div class="flex items-center gap-2">
									<form
										method="POST"
										action="?/submitFeedback"
										use:enhance={() => {
											feedbackSubmitting[idx] = true;
											return async ({ update }) => {
												await update({ reset: false });
												feedbackSubmitting[idx] = false;
												feedbackMap[idx] = 'correct';
											};
										}}
									>
										<input type="hidden" name="fallacyIndex" value={idx} />
										<input type="hidden" name="isCorrect" value="true" />
										<button
											type="submit"
											disabled={submitting}
											class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[11px] font-mono font-bold tracking-wider uppercase border transition-all cursor-pointer"
											style={fb === 'correct'
												? 'background-color: var(--green); border-color: var(--green); color: white;'
												: 'background-color: transparent; border-color: var(--line-2); color: var(--ink-2);'}
										>
											<ThumbsUp class="h-3.5 w-3.5" />
											Tepat
										</button>
									</form>

									<form
										method="POST"
										action="?/submitFeedback"
										use:enhance={() => {
											feedbackSubmitting[idx] = true;
											return async ({ update }) => {
												await update({ reset: false });
												feedbackSubmitting[idx] = false;
												feedbackMap[idx] = 'incorrect';
											};
										}}
									>
										<input type="hidden" name="fallacyIndex" value={idx} />
										<input type="hidden" name="isCorrect" value="false" />
										<button
											type="submit"
											disabled={submitting}
											class="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[11px] font-mono font-bold tracking-wider uppercase border transition-all cursor-pointer"
											style={fb === 'incorrect'
												? 'background-color: var(--red); border-color: var(--red); color: white;'
												: 'background-color: transparent; border-color: var(--line-2); color: var(--ink-2);'}
										>
											<ThumbsDown class="h-3.5 w-3.5" />
											Tidak Tepat
										</button>
									</form>
								</div>
							</div>
						{/if}
					</article>
				{/each}
			</div>
		</div>
	{/if}

	<!-- ══════════════════════════════════════════════════════════
	     5. TRANSCRIPT (collapsible)
	     ══════════════════════════════════════════════════════════ -->
	{#if analysis.transcript}
		<!-- Screen view (Collapsible) -->
		<div class="card mt-4 bg-surface border border-line rounded-card shadow-card overflow-hidden print:hidden">
			<button
				type="button"
				class="w-full flex items-center justify-between p-6 hover:bg-surface-2 transition-colors cursor-pointer text-left"
				onclick={() => (transcriptOpen = !transcriptOpen)}
				aria-expanded={transcriptOpen}
			>
				<div class="flex items-center gap-2.5">
					<FileText class="h-4 w-4 text-red" />
					<span class="font-mono text-xs tracking-widest text-red font-bold uppercase">TRANSKRIP LENGKAP</span>
				</div>
				<div class="flex items-center gap-2 font-mono text-[11px] text-muted uppercase">
					{transcriptOpen ? 'Tutup' : 'Buka'}
					{#if transcriptOpen}
						<ChevronUp class="h-4 w-4" />
					{:else}
						<ChevronDown class="h-4 w-4" />
					{/if}
				</div>
			</button>

			{#if transcriptOpen}
				<div class="px-6 pb-6 pt-2 border-t border-line" transition:slide={{ duration: 250 }}>
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					<p class="text-ink-2 text-[15px] leading-relaxed whitespace-pre-wrap font-sans">{@html transcriptHighlighted()}</p>
					<p class="font-mono text-[10px] text-muted uppercase mt-4">
						<span class="text-red mr-1 font-bold">■</span> Bagian yang disorot mengandung kekeliruan logika yang terdeteksi
					</p>
				</div>
			{/if}
		</div>

		<!-- Print view (Always expanded) -->
		<div class="hidden print:block card mt-6 bg-surface border border-line rounded-card p-6 md:p-8">
			<div class="border-b border-line pb-4 mb-4">
				<span class="font-mono text-xs tracking-widest text-red font-bold uppercase">TRANSKRIP LENGKAP</span>
			</div>
			<!-- eslint-disable-next-line svelte/no-at-html-tags -->
			<p class="text-ink-2 text-sm leading-relaxed whitespace-pre-wrap font-sans">{@html transcriptHighlighted()}</p>
		</div>
	{/if}

	<!-- ══════════════════════════════════════════════════════════
	     6. ACTION BUTTONS
	     ══════════════════════════════════════════════════════════ -->
	<div class="flex flex-wrap items-center justify-end gap-3 mt-6 print:hidden" in:fade={{ duration: 300, delay: 200 }}>
		<button
			type="button"
			class="btn-ghost text-sm py-3 px-5 justify-center cursor-pointer"
			onclick={handleShare}
		>
			{#if shareSuccess}
				<CheckCircle2 class="h-4 w-4 text-green" />
				Tautan Disalin!
			{:else}
				<Share2 class="h-4 w-4" />
				Bagikan Hasil
			{/if}
		</button>

		<button
			type="button"
			class="btn-ghost text-sm py-3 px-5 justify-center cursor-pointer"
			onclick={handleDownloadPdf}
		>
			<Download class="h-4 w-4" />
			Unduh PDF
		</button>

		<a
			href="{base}/fallacy"
			class="btn-primary text-sm py-3 px-5 justify-center"
		>
			<RefreshCw class="h-4 w-4" />
			Analisis Ulang
		</a>
	</div>
</div>
