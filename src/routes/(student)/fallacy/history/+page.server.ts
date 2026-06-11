import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals }) => {
	const session = locals.session;
	const user = locals.user;

	if (!session || !user) {
		throw redirect(303, '/login');
	}

	const supabase = locals.supabase;

	// 1. Parse query parameters
	const page = parseInt(url.searchParams.get('page') || '1', 10);
	const limit = parseInt(url.searchParams.get('limit') || '10', 10);
	const search = url.searchParams.get('search') || '';
	const inputType = url.searchParams.get('inputType') || 'all';
	const fallacyType = url.searchParams.get('fallacyType') || 'all';
	const startDate = url.searchParams.get('startDate') || '';
	const endDate = url.searchParams.get('endDate') || '';

	const offset = (page - 1) * limit;

	// 2. Build Query
	let query = supabase
		.from('fallacy_analyses')
		.select('id, input_type, input_title, total_count, created_at, is_public', { count: 'exact' })
		.eq('user_id', user.id);

	// Filter: Search
	if (search) {
		query = query.or(`input_title.ilike.%${search}%,input_content.ilike.%${search}%`);
	}

	// Filter: Input Type
	if (inputType !== 'all') {
		query = query.eq('input_type', inputType as any);
	}

	// Filter: Fallacy Type
	if (fallacyType !== 'all') {
		query = query.contains('fallacies', [{ name: fallacyType }]);
	}

	// Filter: Date Range
	if (startDate) {
		query = query.gte('created_at', `${startDate}T00:00:00Z`);
	}
	if (endDate) {
		query = query.lte('created_at', `${endDate}T23:59:59Z`);
	}

	// Pagination & Order
	query = query
		.order('created_at', { ascending: false })
		.range(offset, offset + limit - 1);

	const { data: analyses, count: totalCount, error: fetchError } = await query;

	if (fetchError) {
		console.error('Error fetching history:', fetchError);
	}

	return {
		analyses: analyses || [],
		totalCount: totalCount || 0,
		page,
		limit,
		filters: {
			search,
			inputType,
			fallacyType,
			startDate,
			endDate
		}
	};
};
