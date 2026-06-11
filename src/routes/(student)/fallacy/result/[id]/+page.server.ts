import { redirect, error, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const session = locals.session;
	const user = locals.user;

	if (!session || !user) {
		throw redirect(303, '/login');
	}

	const supabase = locals.supabase;

	// 1. Fetch the analysis by ID
	const { data: analysis, error: fetchError } = await supabase
		.from('fallacy_analyses')
		.select('*')
		.eq('id', params.id)
		.maybeSingle();

	if (fetchError || !analysis) {
		throw error(404, {
			message: 'Kasus analisis tidak ditemukan atau sudah dihapus.'
		});
	}

	// 2. Validate ownership (allow read if owner OR public)
	if (analysis.user_id !== user.id && !analysis.is_public) {
		throw error(403, {
			message: 'Anda tidak memiliki hak akses untuk melihat analisis ini.'
		});
	}

	// 3. Fetch existing feedback for this analysis
	const { data: feedbackData } = await supabase
		.from('fallacy_feedback')
		.select('fallacy_index, vote')
		.eq('analysis_id', params.id)
		.eq('user_id', user.id);

	// Map fallacy_index to its correctness feedback value
	const feedbackMap: Record<number, 'correct' | 'incorrect'> = {};
	if (feedbackData) {
		feedbackData.forEach((fb) => {
			feedbackMap[fb.fallacy_index] = fb.vote;
		});
	}

	return {
		analysis,
		feedbackMap
	};
};

export const actions: Actions = {
	submitFeedback: async ({ params, locals, request }) => {
		const user = locals.user;
		const supabase = locals.supabase;

		if (!user) {
			return fail(401, { error: 'Unauthorized. Please login.' });
		}

		const formData = await request.formData();
		const fallacyIndexRaw = formData.get('fallacyIndex') as string;
		const isCorrectRaw = formData.get('isCorrect') as string;

		if (!fallacyIndexRaw || !isCorrectRaw) {
			return fail(400, { error: 'Data masukan tidak lengkap.' });
		}

		const fallacyIndex = parseInt(fallacyIndexRaw, 10);
		const isCorrect = isCorrectRaw === 'true';

		if (isNaN(fallacyIndex)) {
			return fail(400, { error: 'Indeks fallacy tidak valid.' });
		}

		// Insert or update feedback
		const { error: upsertError } = await supabase
			.from('fallacy_feedback')
			.upsert({
				analysis_id: params.id,
				user_id: user.id,
				fallacy_index: fallacyIndex,
				vote: isCorrect ? 'correct' : 'incorrect',
				comment: null // Reserved for detailed feedback input if added later
			}, {
				onConflict: 'analysis_id,user_id,fallacy_index'
			});

		if (upsertError) {
			console.error('Failed to submit feedback:', upsertError);
			return fail(500, { error: 'Gagal merekam feedback ke database.' });
		}

		return { success: true };
	}
};
