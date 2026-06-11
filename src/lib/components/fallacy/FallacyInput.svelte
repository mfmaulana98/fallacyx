<script lang="ts">
	import { 
		FileText, 
		Link2, 
		Video, 
		Mic, 
		ArrowRight, 
		Loader2, 
		Upload, 
		AlertCircle, 
		Trash2, 
		Clock, 
		CheckCircle 
	} from 'lucide-svelte';
	import { enhance } from '$app/forms';
	import { fade } from 'svelte/transition';

	// Component Props
	let {
		onSubmit,
		isLoading = $bindable(false),
		defaultTab = 'text',
		// SvelteKit form/challenge compatibility
		initialType,
		initialUrl = '',
		challengeId = null
	}: {
		onSubmit?: (data: {
			type: 'text' | 'url' | 'youtube' | 'audio';
			value: string | File;
			options?: {
				youtubeRange?: { start: number; end: number } | null;
			};
		}) => void | Promise<void>;
		isLoading?: boolean;
		defaultTab?: 'text' | 'url' | 'youtube' | 'audio';
		initialType?: 'text' | 'url' | 'youtube' | 'audio';
		initialUrl?: string;
		challengeId?: string | null;
	} = $props();

	type TabKey = 'text' | 'url' | 'youtube' | 'audio';

	const tabs: { key: TabKey; label: string; icon: any }[] = [
		{ key: 'text', label: 'Teks', icon: FileText },
		{ key: 'url', label: 'URL Artikel', icon: Link2 },
		{ key: 'youtube', label: 'YouTube', icon: Video },
		{ key: 'audio', label: 'Audio', icon: Mic }
	];

	// Local state management (Svelte 5 Runes)
	let activeTab = $state<TabKey>((initialType || defaultTab) as TabKey);
	
	// Tab 1: Text state
	let inputText = $state('');
	let textError = $state('');
	let textareaEl = $state<HTMLTextAreaElement | null>(null);

	// Tab 2: URL state
	let inputUrl = $state(initialType === 'url' ? initialUrl : '');
	let urlError = $state('');
	let urlPreview = $state<{ title?: string; logo?: string; domain?: string } | null>(null);
	let urlPreviewLoading = $state(false);
	let urlDebounceTimer = $state<ReturnType<typeof setTimeout> | null>(null);

	// Tab 3: YouTube state
	let inputYt = $state(initialType === 'youtube' ? initialUrl : '');
	let ytError = $state('');
	let ytPreview = $state<{ title?: string; thumbnail_url?: string; author_name?: string } | null>(null);
	let ytPreviewLoading = $state(false);
	let ytDebounceTimer = $state<ReturnType<typeof setTimeout> | null>(null);
	
	// Timestamp Range
	let ytStartMin = $state<number | null>(null);
	let ytStartSec = $state<number | null>(null);
	let ytEndMin = $state<number | null>(null);
	let ytEndSec = $state<number | null>(null);

	// Tab 4: Audio state
	let audioFile = $state<File | null>(null);
	let audioError = $state('');
	let audioDuration = $state<number | null>(null);
	let audioDurationStr = $state('');
	let audioUploadProgress = $state(0);
	let isAudioLoading = $state(false);
	let dragOver = $state(false);
	let fileInputEl = $state<HTMLInputElement | null>(null);

	// Sync initial changes if the user starts a daily challenge
	$effect(() => {
		if (initialUrl) {
			if (initialType === 'url') {
				inputUrl = initialUrl;
				triggerUrlFetch(initialUrl);
			}
			if (initialType === 'youtube') {
				inputYt = initialUrl;
				triggerYtFetch(initialUrl);
			}
			if (initialType) activeTab = initialType;
		}
	});

	// Auto-resize for textarea
	$effect(() => {
		if (inputText !== undefined && textareaEl) {
			textareaEl.style.height = 'auto';
			textareaEl.style.height = `${Math.max(200, textareaEl.scrollHeight)}px`;
		}
	});

	// --- Quick Fill Samples ---
	const quickFills = [
		{
			label: 'Serangan Personal (Ad Hominem)',
			text: 'Halah, dia kan cuma mahasiswa kemarin sore yang tidak tahu apa-apa soal ekonomi negara. Kenapa kita harus dengar sarannya tentang inflasi? Pasti motifnya cuma cari ketenaran.'
		},
		{
			label: 'Dilema Palsu (False Dichotomy)',
			text: 'Pilihannya sangat sederhana: kita harus tutup semua pabrik batu bara minggu ini juga, atau bumi ini akan kiamat total tahun depan. Tidak ada jalan tengah!'
		},
		{
			label: 'Himbauan Otoritas (Appeal to Authority)',
			text: 'Kata artis terkenal itu, obat herbal ini bisa menyembuhkan segala penyakit kronis tanpa efek samping, jadi kita tidak butuh dokter lagi. Lagipula, dokter-dokter itu kan cuma ingin mengeruk uang kita.'
		}
	];

	function loadSample(text: string) {
		inputText = text;
		textError = '';
	}

	// --- URL & YouTube Validations & Fetchers ---
	function validateUrl(url: string): boolean {
		try {
			const parsed = new URL(url);
			return parsed.protocol === 'http:' || parsed.protocol === 'https:';
		} catch (_) {
			return false;
		}
	}

	function validateYt(url: string): boolean {
		const ytRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=|embed\/|shorts\/)?([a-zA-Z0-9_-]{11})/;
		return ytRegex.test(url);
	}

	function triggerUrlFetch(url: string) {
		if (urlDebounceTimer) clearTimeout(urlDebounceTimer);
		urlPreview = null;
		
		if (!url || !validateUrl(url)) {
			urlError = url ? 'Format URL tidak valid.' : '';
			return;
		}
		
		urlError = '';
		urlPreviewLoading = true;
		
		urlDebounceTimer = setTimeout(async () => {
			try {
				const response = await fetch(`https://api.microlink.io?url=${encodeURIComponent(url)}`);
				const result = (await response.json()) as any;
				if (result.status === 'success') {
					urlPreview = {
						title: result.data.title || 'Artikel Tanpa Judul',
						logo: result.data.logo?.url || `https://www.google.com/s2/favicons?sz=64&domain=${new URL(url).hostname}`,
						domain: new URL(url).hostname
					};
				} else {
					throw new Error('Microlink failed');
				}
			} catch (_) {
				// Fallback to basic info extraction
				try {
					const host = new URL(url).hostname;
					urlPreview = {
						title: `Halaman Web dari ${host}`,
						logo: `https://www.google.com/s2/favicons?sz=64&domain=${host}`,
						domain: host
					};
				} catch (e) {
					urlError = 'Gagal memuat preview website.';
				}
			} finally {
				urlPreviewLoading = false;
			}
		}, 500);
	}

	function triggerYtFetch(url: string) {
		if (ytDebounceTimer) clearTimeout(ytDebounceTimer);
		ytPreview = null;
		
		if (!url || !validateYt(url)) {
			ytError = url ? 'Format tautan YouTube tidak valid.' : '';
			return;
		}
		
		ytError = '';
		ytPreviewLoading = true;
		
		ytDebounceTimer = setTimeout(async () => {
			try {
				const response = await fetch(`https://noembed.com/embed?url=${encodeURIComponent(url)}`);
				const result = (await response.json()) as any;
				if (result && !result.error) {
					ytPreview = {
						title: result.title,
						thumbnail_url: result.thumbnail_url,
						author_name: result.author_name
					};
				} else {
					throw new Error('Noembed failed');
				}
			} catch (_) {
				ytError = 'Gagal memuat pratinjau video YouTube.';
			} finally {
				ytPreviewLoading = false;
			}
		}, 500);
	}

	// --- Audio Handlers ---
	function handleAudioDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		if (isLoading || isAudioLoading) return;
		
		const files = e.dataTransfer?.files;
		if (files && files.length > 0) {
			processAudioFile(files[0]);
		}
	}

	function handleAudioSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			processAudioFile(target.files[0]);
		}
	}

	function processAudioFile(file: File) {
		audioError = '';
		
		// Validate size (max 50MB)
		const maxSize = 50 * 1024 * 1024;
		if (file.size > maxSize) {
			audioError = 'Ukuran berkas melebihi batas 50MB.';
			return;
		}

		// Validate extension
		const ext = file.name.split('.').pop()?.toLowerCase();
		const validExts = ['mp3', 'mp4', 'wav', 'm4a', 'ogg'];
		if (!validExts.includes(ext || '')) {
			audioError = 'Format berkas tidak didukung. Harap unggah MP3, MP4, WAV, M4A, atau OGG.';
			return;
		}

		audioFile = file;
		isAudioLoading = true;
		audioUploadProgress = 0;

		// Extract Audio Duration
		try {
			const objectURL = URL.createObjectURL(file);
			const audio = new Audio(objectURL);
			audio.addEventListener('loadedmetadata', () => {
				const mins = Math.floor(audio.duration / 60);
				const secs = Math.floor(audio.duration % 60);
				audioDuration = audio.duration;
				audioDurationStr = `${mins}:${secs.toString().padStart(2, '0')}`;
				URL.revokeObjectURL(objectURL);
			});
			audio.addEventListener('error', () => {
				audioDurationStr = 'Durasi tidak dapat dibaca';
				URL.revokeObjectURL(objectURL);
			});
		} catch (_) {
			audioDurationStr = 'Durasi tidak dapat dibaca';
		}

		// Simulate File Upload Progress
		const interval = setInterval(() => {
			audioUploadProgress += Math.random() * 20 + 10;
			if (audioUploadProgress >= 100) {
				audioUploadProgress = 100;
				isAudioLoading = false;
				clearInterval(interval);
			}
		}, 80);
	}

	function removeAudioFile() {
		audioFile = null;
		audioDuration = null;
		audioDurationStr = '';
		audioUploadProgress = 0;
		audioError = '';
		if (fileInputEl) fileInputEl.value = '';
	}

	// --- Form Submission & Validation ---
	function handleFormSubmit(e: SubmitEvent) {
		// Validations
		if (activeTab === 'text') {
			if (!inputText || inputText.trim().length < 10) {
				textError = 'Teks terlalu pendek. Minimal 10 karakter.';
				e.preventDefault();
				return;
			}
			if (inputText.length > 10000) {
				textError = 'Teks terlalu panjang. Maksimal 10.000 karakter.';
				e.preventDefault();
				return;
			}
			textError = '';
		} else if (activeTab === 'url') {
			if (!validateUrl(inputUrl)) {
				urlError = 'Format URL tidak valid. Harus dimulai dengan http:// atau https://';
				e.preventDefault();
				return;
			}
			urlError = '';
		} else if (activeTab === 'youtube') {
			if (!validateYt(inputYt)) {
				ytError = 'Format tautan YouTube tidak valid.';
				e.preventDefault();
				return;
			}
			// Validate optional timestamp range logic
			if (ytStartMin !== null || ytStartSec !== null || ytEndMin !== null || ytEndSec !== null) {
				const startTotal = (ytStartMin || 0) * 60 + (ytStartSec || 0);
				const endTotal = (ytEndMin || 0) * 60 + (ytEndSec || 0);
				if (endTotal > 0 && startTotal >= endTotal) {
					ytError = 'Waktu mulai harus lebih kecil dari waktu selesai.';
					e.preventDefault();
					return;
				}
			}
			ytError = '';
		} else if (activeTab === 'audio') {
			if (!audioFile) {
				audioError = 'Silakan pilih atau unggah berkas audio terlebih dahulu.';
				e.preventDefault();
				return;
			}
			audioError = '';
		}

		// Callback integration
		if (onSubmit) {
			e.preventDefault();
			const range = (ytStartMin !== null || ytStartSec !== null || ytEndMin !== null || ytEndSec !== null)
				? {
					start: (ytStartMin || 0) * 60 + (ytStartSec || 0),
					end: (ytEndMin || 0) * 60 + (ytEndSec || 0)
				}
				: null;
			
			const value = activeTab === 'audio' ? audioFile! : (activeTab === 'text' ? inputText : (activeTab === 'url' ? inputUrl : inputYt));
			onSubmit({
				type: activeTab,
				value,
				options: activeTab === 'youtube' ? { youtubeRange: range } : undefined
			});
		}
	}
</script>

<form
	method="POST"
	action="?/submit"
	enctype="multipart/form-data"
	onsubmit={handleFormSubmit}
	use:enhance={() => {
		isLoading = true;
		return async ({ update }) => {
			await update();
			isLoading = false;
		};
	}}
	class="w-full overflow-hidden rounded-[26px] border bg-surface transition-all duration-300"
	style="border-color: var(--line); box-shadow: var(--shadow-lg);"
>
	<!-- Hidden parameters for compatibility with standard POST action -->
	<input type="hidden" name="inputType" value={activeTab} />
	{#if challengeId}
		<input type="hidden" name="challengeId" value={challengeId} />
	{/if}

	<!-- Tab Headers -->
	<div class="flex flex-wrap gap-1.5 p-3.5 pb-0 border-b" style="border-color: var(--line);">
		{#each tabs as tab}
			<button
				type="button"
				class="flex min-w-[110px] flex-1 items-center justify-center gap-2 rounded-t-[14px] px-3 py-3.5 text-[14px] font-bold transition-all duration-200"
				style={activeTab === tab.key
					? 'color: var(--ink); background: var(--surface-2); box-shadow: inset 0 -3px 0 var(--red);'
					: 'color: var(--muted); background: transparent;'}
				onclick={() => {
					if (!isLoading && !isAudioLoading) activeTab = tab.key;
				}}
				disabled={isLoading || isAudioLoading}
			>
				<tab.icon class="h-[17px] w-[17px]" />
				{tab.label}
			</button>
		{/each}
	</div>

	<!-- Tab Panels with Smooth Transitions -->
	<div class="p-7 min-h-[300px]">
		{#if activeTab === 'text'}
			<div in:fade={{ duration: 150 }} class="space-y-4">
				<div class="flex justify-between items-center">
					<span class="kicker muted block">TEMPEL ARGUMENNYA</span>
					<span class="font-mono text-[11px] {inputText.length > 10000 ? 'text-red font-bold animate-pulse' : 'text-muted'}">
						{inputText.length.toLocaleString('id-ID')} / 10.000 Karakter
					</span>
				</div>

				<textarea
					bind:this={textareaEl}
					name="content"
					class="input min-h-[200px] transition-all duration-200"
					placeholder="Paste teks artikel, caption, speech, atau konten apapun di sini..."
					required
					disabled={isLoading}
					bind:value={inputText}
					maxlength="10500"
				></textarea>

				{#if textError}
					<div class="flex items-center gap-2 text-[13px] text-red font-semibold bg-red-soft rounded-lg px-3 py-2">
						<AlertCircle class="h-4 w-4" />
						{textError}
					</div>
				{/if}

				<!-- Quick Fill / Contoh Cepat -->
				<div class="pt-2">
					<span class="font-mono text-[10px] tracking-wider text-muted uppercase block mb-2">Contoh Cepat Analisis:</span>
					<div class="flex flex-wrap gap-2">
						{#each quickFills as fill}
							<button
								type="button"
								onclick={() => loadSample(fill.text)}
								disabled={isLoading}
								class="text-[12.5px] font-semibold text-ink-2 bg-surface-2 border border-line rounded-lg px-3.5 py-2 text-left hover:border-red hover:text-red transition-all cursor-pointer disabled:opacity-50"
							>
								{fill.label}
							</button>
						{/each}
					</div>
				</div>
			</div>
		{:else if activeTab === 'url'}
			<div in:fade={{ duration: 150 }} class="space-y-4">
				<span class="kicker muted block">TAUTAN ARTIKEL</span>
				<input
					type="url"
					name="content"
					class="input"
					placeholder="https://contoh.com/artikel-opini-yang-viral"
					required
					disabled={isLoading}
					bind:value={inputUrl}
					oninput={(e) => triggerUrlFetch((e.target as HTMLInputElement).value)}
				/>

				{#if urlError}
					<div class="flex items-center gap-2 text-[13px] text-red font-semibold bg-red-soft rounded-lg px-3 py-2">
						<AlertCircle class="h-4 w-4" />
						{urlError}
					</div>
				{/if}

				<!-- Website Link Preview -->
				{#if urlPreviewLoading}
					<div class="flex items-center gap-3 bg-surface-2 border border-line rounded-xl p-4 animate-pulse">
						<Loader2 class="h-5 w-5 animate-spin text-red" />
						<span class="font-mono text-[11px] tracking-wide text-muted uppercase">Memuat detail pratinjau situs...</span>
					</div>
				{:else if urlPreview}
					<div class="flex items-center gap-4 bg-surface-2 border border-line rounded-xl p-4 transition-all duration-300">
						<img 
							src={urlPreview.logo} 
							alt="Favicon" 
							class="h-8 w-8 rounded-md bg-white p-1 border object-contain shrink-0" 
							onerror={(e) => {
								(e.target as HTMLImageElement).src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>';
							}}
						/>
						<div class="overflow-hidden">
							<h4 class="font-bold text-ink text-[15.5px] truncate leading-snug">{urlPreview.title}</h4>
							<p class="font-mono text-[10px] tracking-wide text-muted uppercase mt-0.5">{urlPreview.domain}</p>
						</div>
					</div>
				{/if}

				<p class="font-mono text-[11px] text-muted uppercase">
					Kami ambil teksnya, buang kebisingan, dan periksa nalar di baliknya secara mendalam.
				</p>
			</div>
		{:else if activeTab === 'youtube'}
			<div in:fade={{ duration: 150 }} class="space-y-4">
				<span class="kicker muted block">TAUTAN VIDEO YOUTUBE</span>
				<input
					type="url"
					name="content"
					class="input"
					placeholder="https://youtube.com/watch?v=... atau https://youtu.be/..."
					required
					disabled={isLoading}
					bind:value={inputYt}
					oninput={(e) => triggerYtFetch((e.target as HTMLInputElement).value)}
				/>

				{#if ytError}
					<div class="flex items-center gap-2 text-[13px] text-red font-semibold bg-red-soft rounded-lg px-3 py-2">
						<AlertCircle class="h-4 w-4" />
						{ytError}
					</div>
				{/if}

				<!-- YouTube Preview Card -->
				{#if ytPreviewLoading}
					<div class="flex items-center gap-3 bg-surface-2 border border-line rounded-xl p-4 animate-pulse">
						<Loader2 class="h-5 w-5 animate-spin text-red" />
						<span class="font-mono text-[11px] tracking-wide text-muted uppercase">Membuat pratinjau video YouTube...</span>
					</div>
				{:else if ytPreview}
					<div class="flex flex-col sm:flex-row gap-4 bg-surface-2 border border-line rounded-xl p-4 overflow-hidden transition-all duration-300">
						{#if ytPreview.thumbnail_url}
							<img 
								src={ytPreview.thumbnail_url} 
								alt="YouTube Thumbnail" 
								class="w-full sm:w-36 h-20 object-cover rounded-lg border shrink-0 bg-black"
							/>
						{/if}
						<div class="overflow-hidden flex flex-col justify-center">
							<h4 class="font-bold text-ink text-[15.5px] leading-snug line-clamp-2">{ytPreview.title}</h4>
							<p class="font-mono text-[10px] tracking-wide text-red uppercase mt-1">BY {ytPreview.author_name || 'YouTube Creator'}</p>
						</div>
					</div>
				{/if}

				<!-- Timestamp Range Inputs -->
				<div class="rounded-xl border border-line p-4 bg-surface-2/40">
					<span class="font-mono text-[11px] tracking-wider text-ink font-bold uppercase block mb-3">Rentang Analisis Waktu (Opsional):</span>
					<div class="flex flex-wrap items-center gap-3 text-ink-2">
						<div class="flex items-center gap-2">
							<span class="text-[13px] font-semibold">Mulai:</span>
							<input
								type="number"
								placeholder="0"
								min="0"
								class="input w-16 px-2 py-1 text-center font-mono text-[14px]"
								bind:value={ytStartMin}
								disabled={isLoading}
							/>
							<span class="text-[13px] font-mono">m</span>
							<input
								type="number"
								placeholder="00"
								min="0"
								max="59"
								class="input w-16 px-2 py-1 text-center font-mono text-[14px]"
								bind:value={ytStartSec}
								disabled={isLoading}
							/>
							<span class="text-[13px] font-mono">s</span>
						</div>
						<div class="h-4 w-[1px] bg-line hidden sm:block"></div>
						<div class="flex items-center gap-2">
							<span class="text-[13px] font-semibold">Sampai:</span>
							<input
								type="number"
								placeholder="0"
								min="0"
								class="input w-16 px-2 py-1 text-center font-mono text-[14px]"
								bind:value={ytEndMin}
								disabled={isLoading}
							/>
							<span class="text-[13px] font-mono">m</span>
							<input
								type="number"
								placeholder="00"
								min="0"
								max="59"
								class="input w-16 px-2 py-1 text-center font-mono text-[14px]"
								bind:value={ytEndSec}
								disabled={isLoading}
							/>
							<span class="text-[13px] font-mono">s</span>
						</div>
					</div>
					<p class="mt-2 text-[11.5px] text-muted leading-relaxed">
						Kosongkan jika ingin menganalisis keseluruhan durasi video.
					</p>
				</div>
			</div>
		{:else}
			<div in:fade={{ duration: 150 }} class="space-y-4">
				<span class="kicker muted block">UNGGAH BERKAS AUDIO</span>
				
				<!-- Dropzone -->
				{#if !audioFile}
					<label
						class="relative block cursor-pointer rounded-[18px] border-[1.5px] border-dashed px-6 py-12 text-center transition-all duration-300 overflow-hidden"
						style={dragOver 
							? 'border-color: var(--red); background: rgba(218,43,34,0.03);' 
							: 'border-color: var(--line-2); background: var(--surface-2);'}
						ondragover={(e) => { e.preventDefault(); dragOver = true; }}
						ondragenter={(e) => { e.preventDefault(); dragOver = true; }}
						ondragleave={() => dragOver = false}
						ondrop={handleAudioDrop}
					>
						<div class="mx-auto grid h-14 w-14 place-items-center rounded-2xl text-white transition-transform duration-300" style="background: var(--ink);" class:scale-110={dragOver}>
							<Upload class="h-6 w-6" />
						</div>
						<div class="mt-4 text-[20px] font-black tracking-tight text-ink">Seret & Letakkan atau Cari Berkas</div>
						<div class="mt-2 font-mono text-[11px] tracking-[.08em] text-muted uppercase">
							MP3 · MP4 · WAV · M4A · OGG (Maksimal 50MB)
						</div>
						<input
							bind:this={fileInputEl}
							type="file"
							name="audioFile"
							class="hidden"
							accept=".mp3,.mp4,.wav,.m4a,.ogg,audio/*,video/mp4"
							disabled={isLoading}
							onchange={handleAudioSelect}
						/>
					</label>
				{:else}
					<!-- Uploading / Preview Card -->
					<div class="border border-line rounded-[18px] p-6 bg-surface-2/60 space-y-4">
						<div class="flex items-start justify-between gap-4">
							<div class="flex items-center gap-3">
								<div class="h-11 w-11 rounded-xl bg-ink text-white grid place-items-center shrink-0">
									{#if isAudioLoading}
										<Loader2 class="h-5 w-5 animate-spin text-red" />
									{:else}
										<CheckCircle class="h-5 w-5 text-green" />
									{/if}
								</div>
								<div class="overflow-hidden">
									<h4 class="font-bold text-ink text-[15.5px] truncate max-w-[280px] sm:max-w-md">{audioFile.name}</h4>
									<div class="flex items-center gap-2.5 font-mono text-[10px] text-muted uppercase mt-0.5">
										<span>{(audioFile.size / (1024 * 1024)).toFixed(2)} MB</span>
										<span>•</span>
										<div class="flex items-center gap-1">
											<Clock class="h-3 w-3" />
											<span>{audioDurationStr || 'Membaca durasi...'}</span>
										</div>
									</div>
								</div>
							</div>
							
							<button
								type="button"
								onclick={removeAudioFile}
								disabled={isLoading || isAudioLoading}
								class="h-8 w-8 rounded-full border bg-white border-line grid place-items-center text-muted hover:text-red hover:border-red transition-all cursor-pointer disabled:opacity-50"
								title="Hapus berkas"
							>
								<Trash2 class="h-4 w-4" />
							</button>
						</div>

						<!-- Upload Progress Bar -->
						{#if isAudioLoading || audioUploadProgress < 100}
							<div class="space-y-1.5">
								<div class="flex justify-between font-mono text-[10px] tracking-wide text-muted uppercase">
									<span>Memuat Berkas...</span>
									<span>{Math.round(audioUploadProgress)}%</span>
								</div>
								<div class="h-2 w-full bg-surface-2 border border-line rounded-full overflow-hidden">
									<div class="h-full bg-red rounded-full transition-all duration-100" style="width: {audioUploadProgress}%; background: var(--red);"></div>
								</div>
							</div>
						{/if}
					</div>
				{/if}

				{#if audioError}
					<div class="flex items-center gap-2 text-[13px] text-red font-semibold bg-red-soft rounded-lg px-3 py-2">
						<AlertCircle class="h-4 w-4" />
						{audioError}
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Action Footer / Submit Bar -->
	<div class="flex flex-wrap items-center justify-between gap-4.5 border-t p-6" style="border-color: var(--line); background: var(--surface-2);">
		<span class="max-w-[42ch] font-mono text-[11px] text-muted uppercase leading-relaxed">
			Ajukan argumen Anda ke tribunal logika. Diperiksa secara mendalam dengan akselerator AMD Instinct™ MI300X.
		</span>
		<button
			type="submit"
			class="btn-primary px-7 py-4 text-base cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none min-w-[200px] justify-center"
			disabled={isLoading || isAudioLoading || (activeTab === 'audio' && !audioFile)}
		>
			{#if isLoading}
				<Loader2 class="h-4 w-4 animate-spin text-white mr-2 inline" />
				Memeriksa...
			{:else}
				{activeTab === 'text' ? 'Analisis Teks' : activeTab === 'url' ? 'Analisis Artikel' : activeTab === 'youtube' ? 'Analisis Video' : 'Analisis Audio'}
				<ArrowRight class="h-4 w-4 ml-1.5 inline transition-transform group-hover:translate-x-1" />
			{/if}
		</button>
	</div>
</form>
