<script lang="ts">
	import { ArrowRight, AlertCircle } from 'lucide-svelte';
	import FallacyList from '$lib/components/fallacy/FallacyList.svelte';
	import FallacyEmpty from '$lib/components/fallacy/FallacyEmpty.svelte';
	import type { Fallacy } from '$lib/types/fallacy';

	const MIN_LENGTH = 10;
	const MAX_LENGTH = 10_000;

	type AnalyzeResult = {
		fallacies: Fallacy[];
		overall_assessment: string;
		is_clean: boolean;
		total_count: number;
		overall_severity: 'clean' | 'low' | 'medium' | 'high';
	};

	const SEVERITY_LABEL: Record<AnalyzeResult['overall_severity'], string> = {
		clean: 'TIDAK ADA FALLACY',
		low: 'RINGAN',
		medium: 'SEDANG',
		high: 'SUBSTANSIAL'
	};

	let inputText = $state('');
	let isLoading = $state(false);
	let errorMessage = $state('');
	let result = $state<AnalyzeResult | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		errorMessage = '';

		const trimmed = inputText.trim();
		if (trimmed.length < MIN_LENGTH) {
			errorMessage = `Argumen terlalu pendek. Minimal ${MIN_LENGTH} karakter agar dapat diperiksa.`;
			return;
		}
		if (trimmed.length > MAX_LENGTH) {
			errorMessage = `Argumen terlalu panjang. Maksimal ${MAX_LENGTH.toLocaleString('id-ID')} karakter.`;
			return;
		}

		isLoading = true;
		result = null;

		try {
			const response = await fetch('/api/analyze', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: trimmed })
			});

			const data = (await response.json()) as AnalyzeResult & { message?: string };

			if (!response.ok) {
				throw new Error(data?.message || 'Tribunal gagal memproses argumen ini. Coba lagi.');
			}

			result = data;
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tak terduga. Coba lagi.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Tribunal of Logic · FallacyX</title>
	<meta name="description" content="Submit an argument. Receive a verdict." />
</svelte:head>

<div class="relative min-h-screen overflow-x-hidden py-10">
	<!-- Background glow -->
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

	<div class="page-in relative z-10 mx-auto max-w-[1240px] px-8">
		<!-- Header -->
		<header class="mx-auto mb-12 max-w-[680px] text-center">
			<span class="kicker">TRIBUNAL OF LOGIC</span>
			<h1 class="mt-4 text-[2.6rem] leading-[1.02] font-black tracking-[-.04em] text-balance md:text-[4rem]">
				Serahkan Argumenmu.
			</h1>
			<p class="serif mt-4 text-[1.3rem] text-ink-2 md:text-[1.6rem]">
				Setiap klaim akan diperiksa.
			</p>
		</header>

		<!-- Input Console -->
		<div class="card mx-auto max-w-[820px] p-7 md:p-10" style="background: var(--surface);">
			<form onsubmit={handleSubmit} class="space-y-5">
				<div class="flex items-center justify-between">
					<span class="kicker muted">AJUKAN ARGUMEN</span>
					<span
						class="font-mono text-[11px] {inputText.length > MAX_LENGTH
							? 'animate-pulse font-bold text-red'
							: 'text-muted'}"
					>
						{inputText.length.toLocaleString('id-ID')} / {MAX_LENGTH.toLocaleString('id-ID')} KARAKTER
					</span>
				</div>

				<textarea
					name="content"
					class="input min-h-[220px] text-[1.06rem]"
					placeholder="Tempel klaim, pernyataan, atau argumen yang ingin Anda uji di sini..."
					required
					disabled={isLoading}
					bind:value={inputText}
					maxlength={MAX_LENGTH + 500}
				></textarea>

				{#if errorMessage}
					<div class="flex items-center gap-2 rounded-lg bg-red-soft px-3 py-2 text-[13px] font-semibold text-red">
						<AlertCircle class="h-4 w-4 shrink-0" />
						{errorMessage}
					</div>
				{/if}

				<div class="flex flex-wrap items-center justify-between gap-4 border-t pt-6" style="border-color: var(--line);">
					<span class="max-w-[42ch] font-mono text-[11px] leading-relaxed text-muted uppercase">
						Argumen Anda akan diperiksa oleh tribunal logika menggunakan AMD Instinct™ MI300X.
					</span>

					{#if isLoading}
						<div class="flex min-w-[200px] items-center justify-center gap-3 px-7 py-4">
							<span class="loading-dots" aria-hidden="true">
								<span></span>
								<span></span>
								<span></span>
							</span>
							<span class="serif text-[1.05rem] text-ink-2 italic">Sedang memeriksa...</span>
						</div>
					{:else}
						<button type="submit" class="btn-primary min-w-[200px] justify-center px-7 py-4 text-base">
							PERIKSA SEKARANG
							<ArrowRight class="ml-1 inline h-4 w-4" />
						</button>
					{/if}
				</div>
			</form>
		</div>

		<!-- Verdict -->
		{#if result}
			<section class="mx-auto mt-16 max-w-[820px]">
				<div class="mb-8 flex flex-wrap items-center justify-between gap-3 border-b pb-4" style="border-color: var(--line);">
					<span class="kicker">THE VERDICT</span>
					{#if result.is_clean}
						<span class="badge-clear">{SEVERITY_LABEL.clean}</span>
					{:else}
						<span class="badge-fallacy">
							{result.total_count} {result.total_count > 1 ? 'FALLACIES' : 'FALLACY'} · {SEVERITY_LABEL[result.overall_severity]}
						</span>
					{/if}
				</div>

				{#if result.overall_assessment}
					<blockquote
						class="serif mb-10 border-l-[3px] pl-6 text-[1.3rem] leading-relaxed text-ink italic md:text-[1.5rem]"
						style="border-color: var(--red);"
					>
						{result.overall_assessment}
					</blockquote>
				{/if}

				{#if result.fallacies.length === 0}
					<FallacyEmpty message="Tidak ditemukan kesalahan logika dalam argumen ini." />
				{:else}
					<FallacyList fallacies={result.fallacies} mode="full" showIndex={true} />
				{/if}
			</section>
		{/if}
	</div>
</div>

<style>
	.loading-dots {
		display: inline-flex;
		gap: 6px;
	}

	.loading-dots span {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--red);
		opacity: 0.4;
	}

	@media (prefers-reduced-motion: no-preference) {
		.loading-dots span {
			animation: dot-bounce 1.2s ease-in-out infinite;
		}

		.loading-dots span:nth-child(2) {
			animation-delay: 0.15s;
		}

		.loading-dots span:nth-child(3) {
			animation-delay: 0.3s;
		}

		@keyframes dot-bounce {
			0%,
			80%,
			100% {
				transform: scale(0.6);
				opacity: 0.4;
			}
			40% {
				transform: scale(1);
				opacity: 1;
			}
		}
	}
</style>
