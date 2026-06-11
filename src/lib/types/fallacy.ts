export interface Fallacy {
	// ── New spec fields (FallacyResult) ──────────────────────────────────
	type: string;           // e.g. "ad_hominem"
	type_label: string;     // e.g. "Ad Hominem"
	text: string;           // excerpt sentence
	explanation: string;    // why it's a fallacy
	confidence: number;     // 0.0 – 1.0
	timestamp_start: number | null;   // seconds (for video/audio)
	timestamp_end: number | null;

	// ── Legacy fields (FallacyCard, FallacyChart, FallacyTimeline) ───────
	name?: string;          // same as type_label, kept for backwards compat
	excerpt?: string;       // same as text
	explain?: string;       // same as explanation
	fix?: string;           // suggested better argument
	timestamp?: string;     // formatted "mm:ss" string, kept for FallacyTimeline

	// ── Feedback identifier ───────────────────────────────────────────────
	fallacy_id?: string;    // stable id for feedback voting, falls back to index
}

/** Alias kept for components that expect `FallacyItem` from this module. */
export type FallacyItem = Fallacy;

export type InputType = 'text' | 'url' | 'youtube' | 'audio';

export interface Analysis {
	id: string;
	user_id: string | null;
	input_type: InputType;
	input_content: string;
	input_title: string | null;
	input_hash: string | null;
	transcript: string | null;
	fallacies: Fallacy[];
	total_count: number;
	overall_severity: string | null;
	processing_time_ms: number | null;
	model_version: string | null;
	is_public: boolean;
	metadata: Record<string, any> | null;
	created_at: string;
	updated_at: string;
}

export interface UserStats {
	user_id: string;
	total_analyses: number;
	total_fallacies_found: number;
	current_streak: number;
	longest_streak: number;
	last_analysis_date: string | null;
	fallacy_type_counts: Record<string, number>;
	accuracy_score: number;
	level: number;
	xp_points: number;
	updated_at: string;
}

export interface DailyChallenge {
	id: string;
	challenge_date: string;
	content_url: string;
	content_type: string;
	expected_fallacy_types: string[];
	diamond_reward: number;
	created_at: string;
}

export interface LeaderboardEntry {
	user_id: string;
	username: string | null;
	avatar_url: string | null;
	total_analyses: number;
	total_fallacies_found: number;
	longest_streak: number;
	level: number;
	xp_points: number;
	accuracy_score: number;
}
