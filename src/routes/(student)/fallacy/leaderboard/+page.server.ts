import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { LeaderboardEntry } from '$lib/types/fallacy';

export const load: PageServerLoad = async ({ locals }) => {
	const session = locals.session;
	const user = locals.user;

	if (!session || !user) {
		throw redirect(303, '/login');
	}

	const supabase = locals.supabase;

	let leaderboard: LeaderboardEntry[] = [];

	// 1. Try calling the RPC get_leaderboard function
	const { data: rpcData, error: rpcError } = await supabase
		.rpc('get_leaderboard', { p_limit: 20 });

	if (!rpcError && rpcData) {
		leaderboard = rpcData.map((item: any) => ({
			user_id: item.user_id,
			username: item.username || 'Thinker-' + item.user_id.slice(0, 4).toUpperCase(),
			avatar_url: item.avatar_url,
			total_analyses: item.total_analyses,
			total_fallacies_found: item.total_fallacies_found,
			longest_streak: item.longest_streak,
			level: item.level,
			xp_points: item.xp_points,
			accuracy_score: Number(item.accuracy_score || 0)
		}));
	} else {
		console.warn('Leaderboard RPC call failed, falling back to table query:', rpcError);

		// 2. Fallback table query joining stats with profiles
		const { data: tableData, error: tableError } = await supabase
			.from('user_fallacy_stats')
			.select(`
				user_id,
				total_analyses,
				total_fallacies_found,
				longest_streak,
				level,
				xp_points,
				accuracy_score,
				profiles:user_id (
					username,
					avatar_url
				)
			`)
			.order('xp_points', { ascending: false })
			.limit(20);

		if (tableError) {
			console.error('Leaderboard fallback query failed:', tableError);
		} else if (tableData) {
			leaderboard = (tableData as any[]).map((row) => ({
				user_id: row.user_id,
				username: row.profiles?.username || 'Thinker-' + row.user_id.slice(0, 4).toUpperCase(),
				avatar_url: row.profiles?.avatar_url || null,
				total_analyses: row.total_analyses,
				total_fallacies_found: row.total_fallacies_found,
				longest_streak: row.longest_streak,
				level: row.level,
				xp_points: row.xp_points,
				accuracy_score: Number(row.accuracy_score || 0)
			}));
		}
	}

	return {
		leaderboard
	};
};
