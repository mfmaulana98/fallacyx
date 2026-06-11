<script lang="ts">
	import { Trophy, Shield, Flame, Target, Scale, ArrowLeft, Award } from 'lucide-svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let leaderboard = $derived(data.leaderboard);
	let currentUser = $derived(data.user);

	// Convert 1-20 rank to Roman Numerals for a classical editorial style
	function toRoman(num: number): string {
		const romanMap: Record<number, string> = {
			1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
			6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
			11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
			16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX'
		};
		return romanMap[num] || String(num);
	}
</script>

<svelte:head>
	<title>League of Clear Thinkers · Leaderboard · Revonalar</title>
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
			<span class="kicker">TRIBUNAL LOGIKA · GLOBAL RANKING</span>
			<h1 class="mt-4 text-[2.6rem] md:text-[3.2rem] leading-[1.05] font-black tracking-[-.045em] text-balance">
				League of <span class="serif text-red">Clear Thinkers</span>
			</h1>
			<p class="mt-3.5 text-sm text-ink-2 max-w-xl">
				Daftar 20 pemikir logika terbaik bulan ini yang diurutkan berdasarkan XP points, keaktifan analisis, serta akurasi verifikasi kasus.
			</p>
		</header>

		<!-- Podium Top 3 (Glassmorphism design) -->
		{#if leaderboard.length > 0}
			<section class="grid gap-6 md:grid-cols-3 mb-10">
				<!-- 2nd Place -->
				{#if leaderboard[1]}
					{@const u2 = leaderboard[1]}
					<div class="card p-6 flex flex-col items-center justify-between text-center relative border-line order-2 md:order-1 bg-surface">
						<span class="absolute top-4 left-4 font-mono text-[15px] font-bold text-muted">II</span>
						<div class="flex flex-col items-center mt-2">
							{#if u2.avatar_url}
								<img src={u2.avatar_url} alt={u2.username} class="h-16 w-16 rounded-full border-2 border-line object-cover" />
							{:else}
								<div class="h-16 w-16 rounded-full bg-surface-2 border border-line grid place-items-center text-[20px] font-black text-ink font-mono uppercase">
									{u2.username?.slice(0, 2) || 'TH'}
								</div>
							{/if}
							<h3 class="mt-4 text-[18px] font-black text-ink leading-tight truncate max-w-[15ch]">
								{u2.username}
							</h3>
							<span class="font-mono text-[11px] text-muted uppercase tracking-wider mt-1">LEVEL {u2.level}</span>
						</div>
						<div class="mt-6 pt-4 border-t w-full flex justify-between font-mono text-[12px] text-ink-2" style="border-color: var(--line);">
							<span>{u2.xp_points} XP</span>
							<span class="flex items-center gap-0.5 text-red">
								<Flame class="h-3.5 w-3.5" />
								{u2.longest_streak}d
							</span>
						</div>
					</div>
				{/if}

				<!-- 1st Place (Large Crown Glow) -->
				{#if leaderboard[0]}
					{@const u1 = leaderboard[0]}
					<div
						class="card p-8 flex flex-col items-center justify-between text-center relative order-1 md:order-2 bg-surface"
						style="border-color: var(--red); box-shadow: 0 10px 30px -10px rgba(218, 43, 34, 0.15);"
					>
						<div class="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-red text-white text-[11px] font-mono font-bold tracking-widest px-3 py-1 rounded-full flex items-center gap-1 shadow-md">
							<Trophy class="h-3 w-3" />
							TRIBUNAL KING
						</div>
						<span class="absolute top-4 left-4 font-mono text-[16px] font-bold text-red">I</span>
						<div class="flex flex-col items-center mt-4">
							{#if u1.avatar_url}
								<img src={u1.avatar_url} alt={u1.username} class="h-20 w-20 rounded-full border-2 border-red object-cover shadow-lg" />
							{:else}
								<div class="h-20 w-20 rounded-full bg-red-soft border-2 border-red grid place-items-center text-[24px] font-black text-red font-mono uppercase">
									{u1.username?.slice(0, 2) || 'TH'}
								</div>
							{/if}
							<h3 class="mt-4 text-[21px] font-black text-ink leading-tight truncate max-w-[15ch]">
								{u1.username}
							</h3>
							<span class="font-mono text-[11px] text-red uppercase tracking-widest mt-1">LEVEL {u1.level}</span>
						</div>
						<div class="mt-6 pt-4 border-t w-full flex justify-between font-mono text-[12.5px] text-ink-2" style="border-color: var(--line);">
							<span class="font-bold">{u1.xp_points} XP</span>
							<span class="flex items-center gap-0.5 text-red font-bold">
								<Flame class="h-3.5 w-3.5" />
								{u1.longest_streak}d
							</span>
						</div>
					</div>
				{/if}

				<!-- 3rd Place -->
				{#if leaderboard[2]}
					{@const u3 = leaderboard[2]}
					<div class="card p-6 flex flex-col items-center justify-between text-center relative border-line order-3 bg-surface">
						<span class="absolute top-4 left-4 font-mono text-[15px] font-bold text-muted">III</span>
						<div class="flex flex-col items-center mt-2">
							{#if u3.avatar_url}
								<img src={u3.avatar_url} alt={u3.username} class="h-16 w-16 rounded-full border-2 border-line object-cover" />
							{:else}
								<div class="h-16 w-16 rounded-full bg-surface-2 border border-line grid place-items-center text-[20px] font-black text-ink font-mono uppercase">
									{u3.username?.slice(0, 2) || 'TH'}
								</div>
							{/if}
							<h3 class="mt-4 text-[18px] font-black text-ink leading-tight truncate max-w-[15ch]">
								{u3.username}
							</h3>
							<span class="font-mono text-[11px] text-muted uppercase tracking-wider mt-1">LEVEL {u3.level}</span>
						</div>
						<div class="mt-6 pt-4 border-t w-full flex justify-between font-mono text-[12px] text-ink-2" style="border-color: var(--line);">
							<span>{u3.xp_points} XP</span>
							<span class="flex items-center gap-0.5 text-red">
								<Flame class="h-3.5 w-3.5" />
								{u3.longest_streak}d
							</span>
						</div>
					</div>
				{/if}
			</section>
		{/if}

		<!-- Leaderboard Table -->
		<section class="card p-6 bg-surface overflow-x-auto">
			<div class="border-b pb-4 mb-4 flex items-center justify-between" style="border-color: var(--line);">
				<h3 class="font-mono text-[12px] tracking-[.16em] text-red uppercase">KLASEMEN LOGIKA (TOP 20)</h3>
				<span class="font-mono text-[11px] text-muted uppercase">UPDATE REAL-TIME</span>
			</div>

			<table class="w-full min-w-[700px] border-collapse font-sans text-left">
				<thead>
					<tr class="border-b font-mono text-[11px] tracking-wider text-muted uppercase" style="border-color: var(--line-2);">
						<th class="py-3.5 px-4 font-bold">PERINGKAT</th>
						<th class="py-3.5 px-4 font-bold">PEMIKIR</th>
						<th class="py-3.5 px-4 font-bold text-center">LEVEL</th>
						<th class="py-3.5 px-4 font-bold text-center">KASUS</th>
						<th class="py-3.5 px-4 font-bold text-center">AKURASI</th>
						<th class="py-3.5 px-4 font-bold text-center">MAX STREAK</th>
						<th class="py-3.5 px-4 font-bold text-right">TOTAL XP</th>
					</tr>
				</thead>
				<tbody class="divide-y" style="border-color: var(--line);">
					{#each leaderboard as entry, idx}
						{@const isMe = currentUser && entry.user_id === currentUser.id}
						<tr
							class="transition-colors group"
							style={isMe
								? 'background: var(--red-soft); border-left: 3.5px solid var(--red);'
								: 'background: transparent;'}
						>
							<!-- Rank (Roman numerals) -->
							<td class="py-4 px-4 font-mono text-[14px] font-bold text-ink leading-none">
								{#if idx < 3}
									<span class="text-red font-black">{toRoman(idx + 1)}</span>
								{:else}
									<span class="text-ink-2">{toRoman(idx + 1)}</span>
								{/if}
							</td>

							<!-- Thinker profile -->
							<td class="py-4 px-4">
								<div class="flex items-center gap-3">
									{#if entry.avatar_url}
										<img src={entry.avatar_url} alt={entry.username} class="h-9 w-9 rounded-full object-cover border border-line" />
									{:else}
										<div class="h-9 w-9 rounded-full bg-surface-2 border border-line grid place-items-center text-[13px] font-bold text-ink font-mono uppercase">
											{entry.username?.slice(0, 2) || 'TH'}
										</div>
									{/if}
									<div>
										<span class="font-extrabold text-[15.5px] text-ink block group-hover:text-red transition-all">
											{entry.username}
											{#if isMe}
												<span class="font-mono text-[9.5px] text-white bg-red px-1.5 py-0.5 rounded ml-1 tracking-widest uppercase">ANDA</span>
											{/if}
										</span>
									</div>
								</div>
							</td>

							<!-- Level -->
							<td class="py-4 px-4 text-center font-mono text-[13.5px] font-bold text-ink-2">
								{entry.level}
							</td>

							<!-- Cases examined -->
							<td class="py-4 px-4 text-center font-mono text-[13.5px] text-ink-2">
								{entry.total_analyses}
							</td>

							<!-- Accuracy -->
							<td class="py-4 px-4 text-center">
								<span class="inline-flex items-center gap-1 font-mono text-[12px] font-bold text-green">
									<Target class="h-3 w-3" />
									{Math.round(entry.accuracy_score)}%
								</span>
							</td>

							<!-- Max Streak -->
							<td class="py-4 px-4 text-center">
								<span class="inline-flex items-center gap-1 font-mono text-[12px] font-bold text-red">
									<Flame class="h-3.5 w-3.5" />
									{entry.longest_streak}d
								</span>
							</td>

							<!-- Total XP -->
							<td class="py-4 px-4 text-right font-mono text-[14px] font-bold text-ink">
								{entry.xp_points.toLocaleString('id-ID')} XP
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</section>
	</div>
</div>
