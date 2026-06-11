<script lang="ts">
	import { Upload, Loader2, FileAudio, Clock, AlertCircle, X } from 'lucide-svelte';
	import type { AnalysisResult } from '$lib/api';

	let {
		onAnalysisStart,
		onAnalysisComplete
	}: {
		onAnalysisStart?: (jobId: string) => void;
		onAnalysisComplete?: (result: AnalysisResult) => void;
	} = $props();

	const ACCEPTED_EXTENSIONS = ['mp3', 'mp4', 'wav', 'm4a'];
	const MAX_SIZE_BYTES = 100 * 1024 * 1024; // 100MB

	let file = $state<File | null>(null);
	let durationStr = $state<string | null>(null);
	let dragOver = $state(false);
	let errorMsg = $state('');
	let uploading = $state(false);
	let uploadProgress = $state(0);
	let fileInputEl = $state<HTMLInputElement | null>(null);

	function formatSize(bytes: number): string {
		return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
	}

	function validateFile(candidate: File): string | null {
		const ext = candidate.name.split('.').pop()?.toLowerCase() ?? '';
		if (!ACCEPTED_EXTENSIONS.includes(ext)) {
			return 'Format tidak didukung. Gunakan MP3, MP4, WAV, atau M4A.';
		}
		if (candidate.size > MAX_SIZE_BYTES) {
			return 'File terlalu besar. Maksimal 100MB.';
		}
		return null;
	}

	function readDuration(candidate: File) {
		durationStr = null;
		try {
			const objectUrl = URL.createObjectURL(candidate);
			const audio = new Audio(objectUrl);
			audio.addEventListener('loadedmetadata', () => {
				const mins = Math.floor(audio.duration / 60);
				const secs = Math.floor(audio.duration % 60);
				durationStr = `${mins}:${secs.toString().padStart(2, '0')}`;
				URL.revokeObjectURL(objectUrl);
			});
			audio.addEventListener('error', () => {
				URL.revokeObjectURL(objectUrl);
			});
		} catch {
			durationStr = null;
		}
	}

	function setFile(candidate: File) {
		const validationError = validateFile(candidate);
		if (validationError) {
			errorMsg = validationError;
			return;
		}

		errorMsg = '';
		file = candidate;
		readDuration(candidate);
		uploadFile(candidate);
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		if (uploading) return;

		const dropped = e.dataTransfer?.files?.[0];
		if (dropped) setFile(dropped);
	}

	function handleSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		const selected = target.files?.[0];
		if (selected) setFile(selected);
	}

	function removeFile() {
		file = null;
		durationStr = null;
		errorMsg = '';
		uploadProgress = 0;
		uploading = false;
		if (fileInputEl) fileInputEl.value = '';
	}

	function uploadFile(candidate: File) {
		uploading = true;
		uploadProgress = 0;

		const formData = new FormData();
		formData.append('file', candidate);
		formData.append('inputType', 'audio');

		const xhr = new XMLHttpRequest();

		xhr.upload.addEventListener('progress', (e) => {
			if (e.lengthComputable) {
				uploadProgress = Math.round((e.loaded / e.total) * 100);
			}
		});

		xhr.addEventListener('load', () => {
			uploading = false;

			if (xhr.status < 200 || xhr.status >= 300) {
				errorMsg = 'Upload gagal. Periksa koneksi internet.';
				return;
			}

			try {
				const data = JSON.parse(xhr.responseText);
				if (data?.job_id) {
					onAnalysisStart?.(data.job_id as string);
				} else {
					onAnalysisComplete?.(data as AnalysisResult);
				}
			} catch {
				errorMsg = 'Upload gagal. Periksa koneksi internet.';
			}
		});

		xhr.addEventListener('error', () => {
			uploading = false;
			errorMsg = 'Upload gagal. Periksa koneksi internet.';
		});

		xhr.open('POST', '/api/analyze');
		xhr.send(formData);
	}
</script>

<div class="space-y-4">
	{#if !file}
		<label
			class="relative block cursor-pointer rounded-[18px] border-[1.5px] border-dashed px-6 py-12 text-center transition-all duration-300"
			style={dragOver
				? 'border-color: var(--red); background: rgba(218,43,34,0.03);'
				: 'border-color: var(--line-2); background: var(--surface-2);'}
			ondragover={(e) => {
				e.preventDefault();
				dragOver = true;
			}}
			ondragenter={(e) => {
				e.preventDefault();
				dragOver = true;
			}}
			ondragleave={() => (dragOver = false)}
			ondrop={handleDrop}
		>
			<div
				class="mx-auto grid h-14 w-14 place-items-center rounded-2xl text-white transition-transform duration-300"
				style="background: var(--ink);"
				class:scale-110={dragOver}
			>
				<Upload class="h-6 w-6" />
			</div>
			<div class="mt-4 text-[20px] font-black tracking-tight text-ink">
				Jatuhkan file audio di sini atau klik untuk pilih
			</div>
			<div class="mt-2 font-mono text-[11px] tracking-[.16em] text-muted uppercase">
				MP3 · MP4 · WAV · M4A — Maksimal 100MB
			</div>
			<input
				bind:this={fileInputEl}
				type="file"
				class="hidden"
				accept=".mp3,.mp4,.wav,.m4a,audio/*,video/mp4"
				onchange={handleSelect}
			/>
		</label>
	{:else}
		<div class="space-y-4 rounded-[18px] border border-line bg-surface-2/60 p-6">
			<div class="flex items-start justify-between gap-4">
				<div class="flex items-center gap-3 overflow-hidden">
					<div class="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-ink text-white">
						{#if uploading}
							<Loader2 class="h-5 w-5 animate-spin text-red" />
						{:else}
							<FileAudio class="h-5 w-5" />
						{/if}
					</div>
					<div class="overflow-hidden">
						<h4 class="truncate text-[15.5px] font-bold text-ink">{file.name}</h4>
						<div class="mt-0.5 flex items-center gap-2.5 font-mono text-[10px] uppercase text-muted">
							<span>{formatSize(file.size)}</span>
							<span>•</span>
							<div class="flex items-center gap-1">
								<Clock class="h-3 w-3" />
								<span>{durationStr ?? 'Membaca durasi...'}</span>
							</div>
						</div>
					</div>
				</div>

				<button
					type="button"
					onclick={removeFile}
					disabled={uploading}
					class="grid h-8 w-8 shrink-0 cursor-pointer place-items-center rounded-full border border-line bg-white text-muted transition-all hover:border-red hover:text-red disabled:cursor-not-allowed disabled:opacity-50"
					title="Hapus berkas"
				>
					<X class="h-4 w-4" />
				</button>
			</div>

			{#if uploading}
				<div class="space-y-1.5">
					<div class="flex justify-between font-mono text-[10px] uppercase tracking-wide text-muted">
						<span>Mengunggah berkas...</span>
						<span>{uploadProgress}%</span>
					</div>
					<div class="h-2 w-full overflow-hidden rounded-full border border-line bg-surface-2">
						<div
							class="h-full rounded-full transition-all duration-100"
							style="width: {uploadProgress}%; background: var(--red);"
						></div>
					</div>
				</div>
			{/if}
		</div>
	{/if}

	{#if errorMsg}
		<div class="flex items-center gap-2 rounded-lg bg-red-soft px-3 py-2 text-[13px] font-semibold text-red">
			<AlertCircle class="h-4 w-4" />
			{errorMsg}
		</div>
	{/if}
</div>
