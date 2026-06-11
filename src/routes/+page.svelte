<script lang="ts">
	import { browser } from '$app/environment';
	import { FileText, Link2, Video, Mic, ArrowRight, Check, X, Cpu, Zap, Database } from 'lucide-svelte';

	/* ---------------------------------------------------------
	   LIVE DEMO STATE
	--------------------------------------------------------- */
	type TabKey = 'text' | 'url' | 'youtube' | 'audio';

	const tabs: { key: TabKey; label: string; icon: typeof FileText }[] = [
		{ key: 'text', label: 'Teks', icon: FileText },
		{ key: 'url', label: 'URL Artikel', icon: Link2 },
		{ key: 'youtube', label: 'YouTube', icon: Video },
		{ key: 'audio', label: 'Audio', icon: Mic }
	];

	let activeTab = $state<TabKey>('text');
	let inputText = $state('');
	let inputUrl = $state('');
	let inputYt = $state('');
	let fileName = $state('');

	let isLoading = $state(false);
	let showResult = $state(false);
	let loadMsgIndex = $state(0);
	let progress = $state(0);

	const LOAD_MSGS = [
		'Membaca argumen…',
		'Memisahkan klaim dari kebisingan…',
		'Menelusuri logikanya…',
		'Memeriksa silang setiap klaim…',
		'Menamai fallacy yang ditemukan…',
		'Menyusun putusan…'
	];

	const DAILY_LIMIT = 3;
	let remaining = $state(DAILY_LIMIT);

	const STORAGE_KEY = 'fx_demo_quota';

	function loadQuota() {
		if (!browser) return;
		try {
			const raw = localStorage.getItem(STORAGE_KEY);
			const today = new Date().toISOString().slice(0, 10);
			if (raw) {
				const parsed = JSON.parse(raw);
				if (parsed.date === today) {
					remaining = Math.max(0, DAILY_LIMIT - parsed.used);
					return;
				}
			}
			remaining = DAILY_LIMIT;
		} catch {
			remaining = DAILY_LIMIT;
		}
	}

	function consumeQuota() {
		if (!browser) return;
		const today = new Date().toISOString().slice(0, 10);
		const used = DAILY_LIMIT - remaining + 1;
		localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used }));
		remaining = Math.max(0, DAILY_LIMIT - used);
	}

	$effect(() => {
		loadQuota();
	});

	const MOCK_RESULT = {
		count: 3,
		severity: 'SUBSTANSIAL',
		verdict:
			'Argumen ini terdengar meyakinkan, tapi keropos secara logika — ia membujuk lewat emosi, bukan bukti.',
		fallacies: [
			{
				name: 'Ad Hominem',
				confidence: 0.93,
				excerpt:
					'"Siapa pun yang meragukan kebijakan ini jelas belum pernah baca buku — mereka cuma kesal."',
				explain:
					'Alih-alih menjawab kritik, pembicara menyerang pribadi pengkritik — menyiratkan bahwa mereka bodoh dan emosional. Substansi argumennya sendiri tidak pernah dibahas.',
				fix: 'Hadapi versi terkuat dari kritik tersebut secara langsung. Jika kebijakannya benar-benar baik, ia akan tetap bertahan tanpa perlu menghina orang yang mengkritik.'
			},
			{
				name: 'False Dichotomy',
				confidence: 0.86,
				excerpt: '"Kita cuma punya dua pilihan: terima semuanya, atau negara ini akan hancur tahun depan."',
				explain:
					'Dua pilihan ekstrem disajikan seolah-olah satu-satunya opsi, menghapus segala bentuk kompromi atau alternatif di tengahnya. Kenyataan hampir selalu punya jalan ketiga.',
				fix: 'Akui adanya jalan tengah. Sebutkan setidaknya satu alternatif realistis dan jelaskan kenapa opsi Anda lebih baik — bukan kenapa itu satu-satunya.'
			},
			{
				name: 'Appeal to Authority',
				confidence: 0.74,
				excerpt: '"Profesor ternama sudah mendukung ini, jadi apalagi yang perlu dibuktikan?"',
				explain:
					'Dukungan seorang figur otoritas digunakan sebagai pengganti bukti. Bahkan dukungan ahli sungguhan bukanlah bukti — dan relevansi otoritas tersebut di sini hanya diasumsikan, tidak ditunjukkan.',
				fix: 'Kutip alasan atau data yang dipakai sang ahli, bukan sekadar namanya. Biarkan bukti yang menanggung bobot argumen, bukan gelar.'
			}
		]
	};

	function loadSample() {
		activeTab = 'text';
		inputText =
			'Lihat, siapa pun yang meragukan kebijakan ini jelas belum pernah baca satu buku ekonomi pun — mereka cuma kesal. Pilihannya sederhana: kita terima persis seperti ini, atau seluruh negara akan runtuh tahun depan. Dan profesor ternama dari institut itu sudah mendukungnya, jadi apa lagi buktinya yang dibutuhkan?';
	}

	let loadingTimer: ReturnType<typeof setInterval> | null = null;

	function runDemo() {
		if (isLoading || remaining <= 0) return;
		isLoading = true;
		showResult = false;
		progress = 0;
		loadMsgIndex = 0;

		loadingTimer = setInterval(() => {
			progress += Math.random() * 9 + 5;
			if (progress >= 100) {
				progress = 100;
				const idx = Math.min(LOAD_MSGS.length - 1, Math.floor((progress / 100) * LOAD_MSGS.length));
				loadMsgIndex = idx;
				if (loadingTimer) clearInterval(loadingTimer);
				setTimeout(() => {
					isLoading = false;
					showResult = true;
					consumeQuota();
				}, 450);
			} else {
				const idx = Math.min(LOAD_MSGS.length - 1, Math.floor((progress / 100) * LOAD_MSGS.length));
				loadMsgIndex = idx;
			}
		}, 220);
	}

	function resetDemo() {
		showResult = false;
		progress = 0;
		inputText = '';
		inputUrl = '';
		inputYt = '';
		fileName = '';
	}

	function onFileChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) fileName = target.files[0].name;
	}

	/* ---------------------------------------------------------
	   STATS COUNTER (animate on scroll into view)
	--------------------------------------------------------- */
	function countUp(node: HTMLElement, target: number) {
		let started = false;
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting && !started) {
						started = true;
						const duration = 1400;
						const start = performance.now();
						const fmt = (n: number) =>
							Math.round(n).toLocaleString('id-ID');
						function tick(now: number) {
							const t = Math.min(1, (now - start) / duration);
							const eased = 1 - Math.pow(1 - t, 3);
							node.textContent = fmt(target * eased);
							if (t < 1) requestAnimationFrame(tick);
							else node.textContent = fmt(target);
						}
						requestAnimationFrame(tick);
						observer.disconnect();
					}
				}
			},
			{ threshold: 0.4 }
		);
		observer.observe(node);
		return {
			destroy() {
				observer.disconnect();
			}
		};
	}

	/* ---------------------------------------------------------
	   INPUT TYPE / DETECT CARDS DATA
	--------------------------------------------------------- */
	const inputTypes = [
		{
			icon: FileText,
			title: 'Teks',
			desc: 'Tempel naskah pidato, komentar, esai, atau utas mana pun. Setiap klaim diperiksa silang dalam hitungan detik.'
		},
		{
			icon: Link2,
			title: 'URL Artikel',
			desc: 'Bagikan tautan berita atau opini. Kami ambil isinya, buang gangguan, lalu periksa nalar di baliknya.'
		},
		{
			icon: Video,
			title: 'YouTube',
			desc: 'Tempel tautan video. Audio ditranskrip, lalu setiap jebakan retoris ditandai lengkap dengan kutipan.'
		},
		{
			icon: Mic,
			title: 'Audio',
			desc: 'Unggah rekaman ceramah, podcast, atau diskusi. Cocok untuk memeriksa argumen yang hanya terucap, tak tertulis.'
		}
	];

	const howSteps = [
		{
			no: '01',
			title: 'Tempel URL atau Teks',
			desc: 'Masukkan tautan artikel, video YouTube, rekaman audio, atau tempel langsung naskah argumennya.'
		},
		{
			no: '02',
			title: 'AI Menganalisis di AMD MI300X',
			desc: 'Model bahasa kami membedah setiap klaim, mencari pola logika yang rusak — diproses di atas akselerator AMD Instinct MI300X.'
		},
		{
			no: '03',
			title: 'Lihat Fallacy yang Terdeteksi',
			desc: 'Terima putusan: setiap fallacy diberi nama, diberi skor keyakinan, dan dijelaskan dengan bahasa yang mudah dipahami — lengkap dengan saran perbaikan.'
		}
	];

	const amdAdvantages = [
		{
			icon: Database,
			title: 'Memori Raksasa, Konteks Penuh',
			desc: '192GB HBM3 pada tiap MI300X memungkinkan kami memuat seluruh transkrip video panjang atau artikel utuh dalam satu konteks — tanpa argumen terpotong.'
		},
		{
			icon: Zap,
			title: 'Inferensi Real-Time',
			desc: 'Throughput tinggi berarti hasil pemeriksaan tampil dalam hitungan detik, bukan menit — cocok untuk konsumsi konten yang serba cepat.'
		},
		{
			icon: Cpu,
			title: 'Efisien di Skala Besar',
			desc: 'Efisiensi performa-per-watt MI300X memungkinkan FallacyChecker tetap gratis untuk semua orang, tanpa mengorbankan kedalaman analisis.'
		}
	];
</script>

<svelte:head>
	<title>FallacyChecker · Deteksi Logical Fallacy Real-Time · Revonalar</title>
	<meta
		name="description"
		content="FallacyChecker membaca konten apa pun — teks, artikel, video YouTube, atau audio — dan menamai logika yang rusak di dalamnya, secara real-time."
	/>
</svelte:head>

<div class="relative overflow-x-hidden">
	<!-- Page-wide hero-style glow background -->
	<div class="pointer-events-none fixed inset-0 z-0">
		<div
			class="absolute -top-[340px] -left-[220px] h-[760px] w-[760px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,.20), rgba(218,43,34,0) 62%);"
		></div>
		<div
			class="absolute -right-[120px] -bottom-[220px] h-[520px] w-[520px] rounded-full"
			style="background: radial-gradient(circle, rgba(218,43,34,.12), rgba(218,43,34,0) 62%);"
		></div>
	</div>

	<!-- ================= NAVBAR ================= -->
	<nav
	class="sticky top-0 z-50 border-b"
	style="background: rgba(245,244,240,.78); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border-color: var(--line);"
>
	<div class="mx-auto flex h-[74px] max-w-[1240px] items-center justify-between gap-4 px-8">
		<a href="/" class="flex items-center gap-3">
			<span
				class="relative grid h-[38px] w-[38px] place-items-center overflow-hidden rounded-[11px] text-[20px] font-black text-white"
				style="background: var(--ink);"
			>
				R
				<span
					class="absolute -right-[5px] -bottom-[5px] h-4 w-4 rounded-full"
					style="background: var(--red); filter: blur(.5px);"
				></span>
			</span>
			<span class="leading-tight">
				<b class="block text-[19px] font-black tracking-tight">Revonalar</b>
				<small class="font-mono text-[9.5px] tracking-[.22em] text-muted uppercase">FallacyChecker</small
				>
			</span>
		</a>

		<div class="hidden items-center gap-8 md:flex">
			<a href="#how" class="text-[14.5px] font-semibold text-ink-2 transition-colors hover:text-red">
				Cara Kerja
			</a>
			<a href="#input-types" class="text-[14.5px] font-semibold text-ink-2 transition-colors hover:text-red">
				Jenis Input
			</a>
			<a href="#demo" class="text-[14.5px] font-semibold text-ink-2 transition-colors hover:text-red">
				Coba Demo
			</a>
			<a href="#amd" class="text-[14.5px] font-semibold text-ink-2 transition-colors hover:text-red">
				Teknologi
			</a>
		</div>

		<div class="flex items-center gap-3">
			<a href="#demo" class="btn-ghost hidden sm:inline-flex">Lihat Demo</a>
			<a href="/analyze" class="btn-primary">Coba Sekarang</a>
		</div>
	</div>
</nav>

<!-- ================= HERO ================= -->
<header class="relative pt-16 pb-14 md:pt-[74px] md:pb-14">
	<div class="relative z-10 mx-auto max-w-[1240px] px-8">
		<div class="grid items-start gap-12 lg:grid-cols-[1.08fr_0.92fr] lg:gap-14">
			<div>
				<p class="kicker">Revonalar · Mesin Berpikir Kritis</p>
				<h1 class="mt-5 text-[2.9rem] leading-[1.02] font-black tracking-[-.04em] text-balance md:text-[3.6rem] lg:text-[4.4rem]">
					Deteksi <span class="serif text-red">Logical Fallacy</span> di Konten Apapun, Real-Time
				</h1>
				<p class="mt-6 max-w-[42ch] text-[1.08rem] leading-[1.55] text-ink-2 md:text-[1.22rem]">
					Tonton video YouTube, baca artikel berita, atau scroll media sosial — FallacyX membaca
					argumen di baliknya dan menamai logika yang rusak, lengkap dengan penjelasan dan skor
					keyakinan.
				</p>
				<div class="mt-8 flex flex-wrap items-center gap-3.5">
					<a href="/analyze" class="btn-primary px-7 py-4 text-base">
						Coba Sekarang <ArrowRight class="h-4 w-4" />
					</a>
					<a href="#demo" class="btn-ghost px-7 py-4 text-base">Lihat Demo</a>
				</div>
				<div class="mt-7 flex flex-wrap items-center gap-5 font-mono text-[11.5px] tracking-[.12em] text-muted uppercase">
					<span><b class="font-bold text-ink">Gratis</b>, selamanya</span>
					<span class="h-[5px] w-[5px] rounded-full" style="background: var(--red);"></span>
					<span>Tanpa instal</span>
					<span class="h-[5px] w-[5px] rounded-full" style="background: var(--red);"></span>
					<span>Real-time</span>
				</div>
			</div>

			<!-- HERO MOCKUP -->
			<div class="relative mx-auto mt-6 w-full max-w-[440px] sm:mt-8 lg:mt-2 lg:max-w-none">
				<div
					class="chip absolute -top-[18px] -left-[18px] z-[3] hidden items-center gap-2 rounded-pill border px-4 py-2.5 text-[13.5px] font-bold tracking-tight sm:flex"
					style="background: var(--surface); border-color: var(--line); box-shadow: var(--shadow); transform: rotate(-5deg);"
				>
					<span class="grid h-[18px] w-[18px] place-items-center rounded-full text-[11px] text-white" style="background: var(--green);">
						<Check class="h-3 w-3" />
					</span>
					Argumen valid
				</div>
				<div
					class="chip absolute top-[78px] -right-[18px] z-[3] hidden items-center gap-2 rounded-pill border px-4 py-2.5 text-[13.5px] font-bold tracking-tight sm:flex"
					style="background: var(--surface); border-color: var(--line); box-shadow: var(--shadow); transform: rotate(5deg);"
				>
					<span class="grid h-[18px] w-[18px] place-items-center rounded-full text-[11px] text-white" style="background: var(--red);">
						<X class="h-3 w-3" />
					</span>
					Ad Hominem <span class="font-mono text-[11px] font-normal text-muted">0.93</span>
				</div>

				<div class="rounded-[26px] border p-6" style="background: var(--surface); border-color: var(--line); box-shadow: var(--shadow-lg);">
					<div class="flex items-center justify-between border-b pb-4" style="border-color: var(--line);">
						<span class="flex items-center gap-2 font-mono text-[11px] tracking-[.16em] text-muted uppercase">
							<span class="pulse h-2 w-2 rounded-full" style="background: var(--red);"></span>
							Verdict langsung
						</span>
						<span class="font-mono text-[11px] font-bold text-red">FX · LIVE</span>
					</div>
					<div class="mt-4 flex items-baseline gap-3.5">
						<span class="text-[3.4rem] leading-[.9] font-black tracking-[-.04em]">3</span>
						<span class="font-mono text-[12px] tracking-[.08em] text-ink-2 uppercase">
							fallacy ditemukan<br /><span class="font-bold text-red">Tingkat · Substansial</span>
						</span>
					</div>
					<div class="mt-4 rounded-[14px] border p-4" style="border-color: var(--line); background: var(--surface-2);">
						<div class="flex items-center justify-between">
							<span class="text-[15px] font-extrabold tracking-[-.01em]">Ad Hominem</span>
							<span class="font-mono text-[12px] font-bold text-red">0.93</span>
						</div>
						<div class="mt-2.5 h-1.5 overflow-hidden rounded-full" style="background: rgba(21,20,26,.08);">
							<div class="h-full rounded-full" style="width: 93%; background: var(--red);"></div>
						</div>
						<p class="serif mt-2.5 text-[13.5px] leading-[1.4] text-ink-2">
							"Siapa pun yang meragukan ini jelas belum pernah baca buku — mereka cuma kesal."
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</header>

<!-- ================= HOW IT WORKS ================= -->
<section id="how" class="py-16 md:py-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="mb-11 max-w-[760px]">
			<p class="kicker">Cara Kerja</p>
			<h2 class="mt-3.5 text-[2.1rem] font-black tracking-[-.035em] text-balance md:text-[2.8rem]">
				Tiga langkah, dari <span class="serif">konten mentah</span> ke putusan logika.
			</h2>
			<p class="mt-4 max-w-[54ch] text-[1.08rem] text-ink-2 md:text-[1.14rem]">
				Tidak perlu transkrip, tidak perlu unggah berlapis. Cukup beri kami sumbernya.
			</p>
		</div>
		<div class="grid gap-5 md:grid-cols-3">
			{#each howSteps as step}
				<div class="card p-7">
					<span class="font-mono text-[13px] font-bold tracking-[.1em] text-red">{step.no}</span>
					<h3 class="mt-4 text-[1.5rem] font-extrabold tracking-[-.02em]">{step.title}</h3>
					<p class="mt-2.5 text-[1.02rem] text-ink-2">{step.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ================= INPUT TYPES ================= -->
<section id="input-types" class="pt-0 pb-16 md:pb-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="mb-11 max-w-[760px]">
			<p class="kicker">Jenis Input</p>
			<h2 class="mt-3.5 text-[2.1rem] font-black tracking-[-.035em] text-balance md:text-[2.8rem]">
				Empat pintu masuk, <span class="serif">satu pemeriksaan.</span>
			</h2>
			<p class="mt-4 max-w-[54ch] text-[1.08rem] text-ink-2 md:text-[1.14rem]">
				Dari mana pun konten itu berasal — kami siap memeriksanya.
			</p>
		</div>
		<div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
			{#each inputTypes as item}
				<div class="card p-6">
					<div class="icon-tile grid h-[54px] w-[54px] place-items-center rounded-[15px]" style="background: var(--ink); color: #fff;">
						<item.icon class="h-6 w-6" />
					</div>
					<h3 class="mt-5 text-[1.25rem] font-extrabold tracking-[-.02em]">{item.title}</h3>
					<p class="mt-2 text-[.96rem] text-ink-2">{item.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ================= LIVE DEMO ================= -->
<section id="demo" class="pt-0 pb-16 md:pb-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="mx-auto mb-11 max-w-[760px] text-center">
			<p class="kicker mx-auto">Bagian IV · Pemeriksaan</p>
			<h2 class="mt-3.5 text-[2.1rem] font-black tracking-[-.035em] text-balance md:text-[2.8rem]">
				Coba <span class="serif">FallacyChecker</span> sekarang.
			</h2>
			<p class="mx-auto mt-4 max-w-[54ch] text-[1.08rem] text-ink-2 md:text-[1.14rem]">
				Tempelkan argumen, tautan, atau unggah rekaman. Tidak perlu akun — dibatasi {DAILY_LIMIT}× per hari.
			</p>
		</div>

		<div class="mx-auto max-w-[880px] overflow-hidden rounded-[26px] border" style="background: var(--surface); border-color: var(--line); box-shadow: var(--shadow-lg);">
			<!-- tabs -->
			<div class="flex flex-wrap gap-1.5 p-3.5 pb-0">
				{#each tabs as tab}
					<button
						class="flex min-w-[110px] flex-1 items-center justify-center gap-2 rounded-tab px-3 py-3.5 text-[14px] font-bold transition-colors"
						style={activeTab === tab.key
							? 'color: var(--ink); background: var(--surface-2); box-shadow: inset 0 -3px 0 var(--red);'
							: 'color: var(--muted); background: transparent;'}
						onclick={() => (activeTab = tab.key)}
					>
						<tab.icon class="h-[17px] w-[17px]" />
						{tab.label}
					</button>
				{/each}
			</div>

			<div class="border-t" style="border-color: var(--line);">
				{#if !showResult}
					<div class="p-7">
						{#if activeTab === 'text'}
							<span class="kicker muted mb-3 block text-muted!">Tempel argumennya</span>
							<textarea
								class="input min-h-[170px] resize-y"
								placeholder="Tempel pidato, komentar, artikel, atau utas — apa pun yang mengklaim membuat sebuah poin…"
								bind:value={inputText}
							></textarea>
							<p class="mt-3 font-mono text-[11px] text-muted">
								Mulai dari halaman kosong?
								<button class="cursor-pointer border-b text-red" style="border-color: var(--red);" onclick={loadSample}>
									Muat contoh argumen →
								</button>
							</p>
						{:else if activeTab === 'url'}
							<span class="kicker muted mb-3 block text-muted!">Tautan artikel</span>
							<input
								class="input"
								type="text"
								placeholder="https://contoh.com/artikel-opini-yang-viral"
								bind:value={inputUrl}
							/>
							<p class="mt-3 font-mono text-[11px] text-muted">
								Kami ambil teksnya, buang gangguan, dan periksa nalar di baliknya.
							</p>
						{:else if activeTab === 'youtube'}
							<span class="kicker muted mb-3 block text-muted!">Tautan YouTube</span>
							<input class="input" type="text" placeholder="https://youtube.com/watch?v=…" bind:value={inputYt} />
							<p class="mt-3 font-mono text-[11px] text-muted">
								Audio akan ditranskrip lalu setiap jebakan retoris ditandai lengkap timestamp.
							</p>
						{:else}
							<span class="kicker muted mb-3 block text-muted!">Unggah audio atau dokumen</span>
							<label
								class="block cursor-pointer rounded-[18px] border-[1.5px] border-dashed px-6 py-10 text-center transition-colors"
								style="border-color: var(--line-2); background: var(--surface-2);"
							>
								<div class="mx-auto grid h-14 w-14 place-items-center rounded-2xl text-white" style="background: var(--ink);">
									<Mic class="h-6 w-6" />
								</div>
								<div class="mt-4 text-[1.25rem] font-extrabold tracking-[-.02em]">Klik untuk pilih berkas</div>
								<div class="mt-2 font-mono text-[11px] tracking-[.08em] text-muted uppercase">
									MP3 · WAV · M4A · PDF · DOCX · TXT
								</div>
								{#if fileName}
									<div class="mt-3.5 font-mono text-[13px] font-bold text-red">✓ {fileName}</div>
								{/if}
								<input type="file" class="hidden" accept=".mp3,.wav,.m4a,.pdf,.docx,.txt,audio/*" onchange={onFileChange} />
							</label>
						{/if}
					</div>

					<!-- runbar -->
					<div class="flex flex-wrap items-center justify-between gap-4.5 border-t p-6" style="border-color: var(--line); background: var(--surface-2);">
						<span class="max-w-[38ch] font-mono text-[11px] text-muted uppercase">
							{#if remaining > 0}
								Sisa pemeriksaan gratis hari ini: <b class="text-ink">{remaining}/{DAILY_LIMIT}</b>. Tidak perlu akun.
							{:else}
								Jatah gratis hari ini habis. Kembali besok, atau buat akun untuk akses penuh.
							{/if}
						</span>
						{#if remaining > 0}
							<button class="btn-primary px-7 py-4 text-base" onclick={runDemo} disabled={isLoading}>
								Periksa Argumen <ArrowRight class="h-4 w-4" />
							</button>
						{:else}
							<a href="/login" class="btn-primary px-7 py-4 text-base">
								Buat Akun Gratis <ArrowRight class="h-4 w-4" />
							</a>
						{/if}
					</div>

					{#if isLoading}
						<div class="border-t p-12 text-center md:p-16" style="border-color: var(--line);">
							<div class="mx-auto h-2 max-w-[520px] overflow-hidden rounded-lg" style="background: var(--surface-2);">
								<div class="h-full rounded-lg transition-[width] duration-200" style="width: {progress}%; background: var(--red);"></div>
							</div>
							<div class="mt-3.5 font-mono text-[11px] tracking-[.16em] text-muted">{Math.round(progress)}%</div>
							<div class="serif mt-6 min-h-[1.3em] text-[1.4rem] md:text-[1.8rem]">{LOAD_MSGS[loadMsgIndex]}</div>
						</div>
					{/if}
				{:else}
					<!-- RESULTS -->
					<div class="page-in">
						<div class="dark-section p-7 md:p-9">
							<div class="flex flex-wrap justify-between gap-3 border-b pb-5 font-mono text-[11px] tracking-[.14em] text-on-dark-mut uppercase" style="border-color: rgba(244,242,238,.14);">
								<span>Tribunal menyatakan —</span>
								<span>Diperiksa <b class="text-on-dark">{new Date().toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })}</b></span>
							</div>
							<div class="mt-6 grid grid-cols-2 items-center gap-8 md:grid-cols-[auto_auto_1fr]">
								<div>
									<div class="text-[3.4rem] leading-[.85] font-black tracking-[-.04em] text-on-dark">{MOCK_RESULT.count}</div>
									<div class="mt-2 font-mono text-[10px] tracking-[.14em] text-on-dark-mut uppercase">Fallacy ditemukan</div>
								</div>
								<div>
									<div class="text-[1.9rem] font-black tracking-[-.03em] text-red">{MOCK_RESULT.severity}</div>
									<div class="mt-2 font-mono text-[10px] tracking-[.14em] text-on-dark-mut uppercase">Tingkat keparahan</div>
								</div>
								<div class="serif col-span-2 text-[1.3rem] leading-[1.25] text-on-dark md:col-span-1 md:text-[1.4rem]">
									{MOCK_RESULT.verdict}
								</div>
							</div>
						</div>

						<div class="px-7 py-3.5 md:px-9">
							{#each MOCK_RESULT.fallacies as f, i}
								<article class="border-b py-7 last:border-b-0" style="border-color: var(--line);">
									<div class="flex flex-wrap items-center justify-between gap-4">
										<div class="flex items-center gap-3.5">
											<span class="badge-fallacy rounded-[9px]! px-0! py-0! grid h-[30px] w-[30px] place-items-center font-extrabold">
												<X class="h-4 w-4" />
											</span>
											<h3 class="text-[1.4rem] font-extrabold tracking-[-.025em] md:text-[1.55rem]">
												{String(i + 1).padStart(2, '0')} · {f.name}
											</h3>
										</div>
										<div class="text-right">
											<div class="font-mono text-[14px] font-bold text-red">{f.confidence.toFixed(2)}</div>
											<div class="mt-1.5 h-1.5 w-[120px] overflow-hidden rounded-full" style="background: rgba(21,20,26,.08);">
												<div class="h-full rounded-full" style="width: {Math.round(f.confidence * 100)}%; background: var(--red);"></div>
											</div>
										</div>
									</div>
									<span class="kicker muted mt-4.5 mb-1.5 block text-muted!">Kutipan pemicu</span>
									<p class="serif rounded-r-xl border-l-[3px] px-5 py-3.5" style="background: var(--surface-2); border-color: var(--red);">
										{f.excerpt}
									</p>
									<span class="kicker muted mt-4.5 mb-1.5 block text-muted!">Kenapa ini keliru</span>
									<p class="text-ink-2">{f.explain}</p>
									<div class="mt-3.5 rounded-[14px] p-4" style="background: var(--red-soft);">
										<span class="kicker mb-0 block text-red!">Argumen yang lebih kuat akan</span>
										<p class="mt-1 text-ink">{f.fix}</p>
									</div>
								</article>
							{/each}
						</div>

						<div class="border-t p-8 text-center" style="border-color: var(--line); background: var(--surface-2);">
							<button class="btn-secondary px-7 py-4 text-base" onclick={resetDemo}>↺ Periksa argumen lain</button>
							<p class="mt-5 font-mono text-[12px] text-muted">
								Ingin riwayat &amp; statistik tersimpan?
								<a href="/login" class="border-b text-red" style="border-color: var(--red);">Buat akun gratis →</a>
							</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</section>

<!-- ================= STATS COUNTER ================= -->
<section class="pt-0 pb-16 md:pb-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="dark-section px-6 py-14 md:px-12 md:py-16">
			<div class="mb-10 max-w-[640px]">
				<p class="kicker">Sejauh Ini</p>
				<h2 class="mt-3.5 text-[2rem] font-black tracking-[-.03em] text-on-dark md:text-[2.6rem]">
					Sebuah gerakan, <span class="serif text-on-dark">terhitung satu argumen.</span>
				</h2>
			</div>
			<div class="grid gap-6 sm:grid-cols-3">
				<div class="glass rounded-[20px] p-7">
					<span class="font-mono text-[13px] font-bold tracking-[.1em] text-red">01</span>
					<h3 class="mt-4 text-[2.6rem] font-black tracking-[-.03em] text-on-dark">
						<span use:countUp={128430}>0</span>+
					</h3>
					<p class="mt-2 text-on-dark-mut">Analisis dilakukan</p>
				</div>
				<div class="glass rounded-[20px] p-7">
					<span class="font-mono text-[13px] font-bold tracking-[.1em] text-red">02</span>
					<h3 class="mt-4 text-[2.6rem] font-black tracking-[-.03em] text-on-dark">
						<span use:countUp={304871}>0</span>+
					</h3>
					<p class="mt-2 text-on-dark-mut">Fallacy terdeteksi</p>
				</div>
				<div class="glass rounded-[20px] p-7">
					<span class="font-mono text-[13px] font-bold tracking-[.1em] text-red">03</span>
					<h3 class="mt-4 text-[2.6rem] font-black tracking-[-.03em] text-on-dark">
						<span use:countUp={42619}>0</span>+
					</h3>
					<p class="mt-2 text-on-dark-mut">Pengguna aktif</p>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- ================= POWERED BY AMD ================= -->
<section id="amd" class="pt-0 pb-16 md:pb-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="mb-11 max-w-[760px]">
			<p class="kicker">Ditenagai Oleh</p>
			<h2 class="mt-3.5 text-[2.1rem] font-black tracking-[-.035em] text-balance md:text-[2.8rem]">
				Dibangun di atas <span class="serif">AMD Instinct MI300X.</span>
			</h2>
			<p class="mt-4 max-w-[54ch] text-[1.08rem] text-ink-2 md:text-[1.14rem]">
				Memeriksa logika sebuah video panjang atau artikel utuh secara real-time butuh memori besar
				dan throughput tinggi. MI300X memberi keduanya — sehingga FallacyX bisa tetap cepat,
				mendalam, dan gratis.
			</p>
		</div>
		<div class="grid gap-5 md:grid-cols-3">
			{#each amdAdvantages as item}
				<div class="card p-7">
					<div class="icon-tile grid h-[54px] w-[54px] place-items-center rounded-[15px]" style="background: var(--red); color: #fff; box-shadow: 0 8px 20px -8px rgba(218,43,34,.6);">
						<item.icon class="h-6 w-6" />
					</div>
					<h3 class="mt-5 text-[1.3rem] font-extrabold tracking-[-.02em]">{item.title}</h3>
					<p class="mt-2.5 text-[1rem] text-ink-2">{item.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ================= CTA FINAL ================= -->
<section class="pt-0 pb-16 md:pb-[88px]">
	<div class="mx-auto max-w-[1240px] px-8">
		<div class="dark-section px-6 py-14 text-center md:px-12 md:py-20">
			<p class="kicker mx-auto">Bergabunglah dengan tribunal</p>
			<h2 class="mx-auto mt-3.5 max-w-[18ch] text-[2.4rem] font-black tracking-[-.035em] text-on-dark md:text-[3.6rem]">
				Berhenti menelan argumen <span class="serif text-on-dark">mentah-mentah.</span>
			</h2>
			<p class="mx-auto mt-5 max-w-[54ch] text-[1.1rem] text-on-dark-mut md:text-[1.2rem]">
				Buat akun gratis untuk menyimpan riwayat pemeriksaan, melacak progres, dan mengakses
				pemeriksaan tanpa batas harian.
			</p>
			<div class="mt-8 flex flex-wrap items-center justify-center gap-3.5">
				<a href="/login" class="btn-primary px-8 py-4 text-base">
					Mulai Gratis <ArrowRight class="h-4 w-4" />
				</a>
				<a href="/analyze" class="btn-ghost-ondark px-8 py-4 text-base">Coba Tanpa Akun</a>
			</div>
		</div>
	</div>
</section>

<!-- ================= FOOTER ================= -->
<footer style="background: var(--dark); color: var(--on-dark);">
	<div class="mx-auto max-w-[1240px] px-8 py-14 md:py-16">
		<div class="flex flex-wrap items-start justify-between gap-10 border-b pb-10" style="border-color: rgba(244,242,238,.12);">
			<div>
				<div class="text-[2.4rem] font-black tracking-[-.04em]">
					Fallacy<span class="text-red">Checker</span>
				</div>
				<p class="mt-4 max-w-[36ch] text-on-dark-mut">
					Mesin berpikir kritis dari Revonalar. Tempel apa pun, terima putusan logikanya — gratis,
					real-time, dan tanpa basa-basi.
				</p>
			</div>
			<div class="serif max-w-[14ch] text-[1.7rem] text-right text-on-dark md:text-left">
				Berpikirlah, atau orang lain yang akan berpikir untukmu.
			</div>
		</div>
		<div class="mt-6 flex flex-wrap justify-between gap-5 font-mono text-[11px] tracking-[.1em] text-on-dark-mut uppercase">
			<span>© 2026 Revonalar · Nalar adalah revolusi yang sesungguhnya</span>
			<span>Dibangun untuk AMD Developer Hackathon 2026</span>
		</div>
	</div>
	</footer>
</div>
