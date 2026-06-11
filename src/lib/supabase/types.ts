// Database type definitions matching Supabase migrations
// Saved to: src/lib/supabase/types.ts

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export type FallacyInputType = 'text' | 'url' | 'youtube' | 'audio';

export interface Database {
	public: {
		Tables: {
			profiles: {
				Row: {
					id: string;
					username: string | null;
					full_name: string | null;
					avatar_url: string | null;
					created_at: string;
					updated_at: string;
				};
				Insert: {
					id: string;
					username?: string | null;
					full_name?: string | null;
					avatar_url?: string | null;
					created_at?: string;
					updated_at?: string;
				};
				Update: {
					id?: string;
					username?: string | null;
					full_name?: string | null;
					avatar_url?: string | null;
					created_at?: string;
					updated_at?: string;
				};
				Relationships: [];
			};
			fallacy_analyses: {
				Row: {
					id: string;
					user_id: string | null;
					input_type: FallacyInputType;
					input_content: string;
					input_title: string | null;
					input_hash: string | null;
					transcript: string | null;
					fallacies: Json;
					total_count: number;
					overall_severity: string | null;
					processing_time_ms: number | null;
					model_version: string | null;
					is_public: boolean;
					metadata: Json;
					created_at: string;
					updated_at: string;
				};
				Insert: {
					id?: string;
					user_id?: string | null;
					input_type: FallacyInputType;
					input_content: string;
					input_title?: string | null;
					input_hash?: string | null;
					transcript?: string | null;
					fallacies?: Json;
					total_count?: number;
					overall_severity?: string | null;
					processing_time_ms?: number | null;
					model_version?: string | null;
					is_public?: boolean;
					metadata?: Json;
					created_at?: string;
					updated_at?: string;
				};
				Update: {
					id?: string;
					user_id?: string | null;
					input_type?: FallacyInputType;
					input_content?: string;
					input_title?: string | null;
					input_hash?: string | null;
					transcript?: string | null;
					fallacies?: Json;
					total_count?: number;
					overall_severity?: string | null;
					processing_time_ms?: number | null;
					model_version?: string | null;
					is_public?: boolean;
					metadata?: Json;
					created_at?: string;
					updated_at?: string;
				};
				Relationships: [
					{
						foreignKeyName: 'fallacy_analyses_user_id_fkey';
						columns: ['user_id'];
						isOneToOne: false;
						referencedRelation: 'profiles';
						referencedColumns: ['id'];
					}
				];
			};
			fallacy_vectors: {
				Row: {
					id: string;
					analysis_id: string;
					fallacy_type: string;
					fallacy_text: string;
					embedding_id: string | null;
					created_at: string;
				};
				Insert: {
					id?: string;
					analysis_id: string;
					fallacy_type: string;
					fallacy_text: string;
					embedding_id?: string | null;
					created_at?: string;
				};
				Update: {
					id?: string;
					analysis_id?: string;
					fallacy_type?: string;
					fallacy_text?: string;
					embedding_id?: string | null;
					created_at?: string;
				};
				Relationships: [
					{
						foreignKeyName: 'fallacy_vectors_analysis_id_fkey';
						columns: ['analysis_id'];
						isOneToOne: false;
						referencedRelation: 'fallacy_analyses';
						referencedColumns: ['id'];
					}
				];
			};
			fallacy_feedback: {
				Row: {
					id: string;
					analysis_id: string;
					user_id: string | null;
					fallacy_index: number;
					vote: 'correct' | 'incorrect';
					comment: string | null;
					created_at: string;
				};
				Insert: {
					id?: string;
					analysis_id: string;
					user_id?: string | null;
					fallacy_index: number;
					vote: 'correct' | 'incorrect';
					comment?: string | null;
					created_at?: string;
				};
				Update: {
					id?: string;
					analysis_id?: string;
					user_id?: string | null;
					fallacy_index?: number;
					vote?: 'correct' | 'incorrect';
					comment?: string | null;
					created_at?: string;
				};
				Relationships: [
					{
						foreignKeyName: 'fallacy_feedback_analysis_id_fkey';
						columns: ['analysis_id'];
						isOneToOne: false;
						referencedRelation: 'fallacy_analyses';
						referencedColumns: ['id'];
					},
					{
						foreignKeyName: 'fallacy_feedback_user_id_fkey';
						columns: ['user_id'];
						isOneToOne: false;
						referencedRelation: 'profiles';
						referencedColumns: ['id'];
					}
				];
			};
			user_fallacy_stats: {
				Row: {
					user_id: string;
					total_analyses: number;
					total_fallacies_found: number;
					current_streak: number;
					longest_streak: number;
					last_analysis_date: string | null;
					fallacy_type_counts: Json;
					accuracy_score: number;
					level: number;
					xp_points: number;
					updated_at: string;
				};
				Insert: {
					user_id: string;
					total_analyses?: number;
					total_fallacies_found?: number;
					current_streak?: number;
					longest_streak?: number;
					last_analysis_date?: string | null;
					fallacy_type_counts?: Json;
					accuracy_score?: number;
					level?: number;
					xp_points?: number;
					updated_at?: string;
				};
				Update: {
					user_id?: string;
					total_analyses?: number;
					total_fallacies_found?: number;
					current_streak?: number;
					longest_streak?: number;
					last_analysis_date?: string | null;
					fallacy_type_counts?: Json;
					accuracy_score?: number;
					level?: number;
					xp_points?: number;
					updated_at?: string;
				};
				Relationships: [
					{
						foreignKeyName: 'user_fallacy_stats_user_id_fkey';
						columns: ['user_id'];
						isOneToOne: true;
						referencedRelation: 'profiles';
						referencedColumns: ['id'];
					}
				];
			};
			fallacy_achievements: {
				Row: {
					id: string;
					user_id: string;
					achievement_code: string;
					unlocked_at: string;
					diamond_reward: number;
				};
				Insert: {
					id?: string;
					user_id: string;
					achievement_code: string;
					unlocked_at?: string;
					diamond_reward?: number;
				};
				Update: {
					id?: string;
					user_id?: string;
					achievement_code?: string;
					unlocked_at?: string;
					diamond_reward?: number;
				};
				Relationships: [
					{
						foreignKeyName: 'fallacy_achievements_user_id_fkey';
						columns: ['user_id'];
						isOneToOne: false;
						referencedRelation: 'profiles';
						referencedColumns: ['id'];
					}
				];
			};
			daily_fallacy_challenges: {
				Row: {
					id: string;
					challenge_date: string;
					content_url: string;
					content_type: string;
					expected_fallacy_types: string[];
					diamond_reward: number;
					created_at: string;
				};
				Insert: {
					id?: string;
					challenge_date: string;
					content_url: string;
					content_type: string;
					expected_fallacy_types: string[];
					diamond_reward?: number;
					created_at?: string;
				};
				Update: {
					id?: string;
					challenge_date?: string;
					content_url?: string;
					content_type?: string;
					expected_fallacy_types?: string[];
					diamond_reward?: number;
					created_at?: string;
				};
				Relationships: [];
			};
			daily_challenge_submissions: {
				Row: {
					id: string;
					user_id: string;
					challenge_id: string;
					analysis_id: string;
					completed_at: string;
				};
				Insert: {
					id?: string;
					user_id: string;
					challenge_id: string;
					analysis_id: string;
					completed_at?: string;
				};
				Update: {
					id?: string;
					user_id?: string;
					challenge_id?: string;
					analysis_id?: string;
					completed_at?: string;
				};
				Relationships: [
					{
						foreignKeyName: 'daily_challenge_submissions_user_id_fkey';
						columns: ['user_id'];
						isOneToOne: false;
						referencedRelation: 'profiles';
						referencedColumns: ['id'];
					},
					{
						foreignKeyName: 'daily_challenge_submissions_challenge_id_fkey';
						columns: ['challenge_id'];
						isOneToOne: false;
						referencedRelation: 'daily_fallacy_challenges';
						referencedColumns: ['id'];
					},
					{
						foreignKeyName: 'daily_challenge_submissions_analysis_id_fkey';
						columns: ['analysis_id'];
						isOneToOne: false;
						referencedRelation: 'fallacy_analyses';
						referencedColumns: ['id'];
					}
				];
			};
		};
		Views: {
			public_analyses: {
				Row: Database['public']['Tables']['fallacy_analyses']['Row'];
				Relationships: Database['public']['Tables']['fallacy_analyses']['Relationships'];
			};
		};
		Functions: {
			get_leaderboard: {
				Args: {
					p_limit?: number;
				};
				Returns: {
					user_id: string;
					username: string | null;
					avatar_url: string | null;
					total_analyses: number;
					total_fallacies_found: number;
					longest_streak: number;
					level: number;
					xp_points: number;
					accuracy_score: number;
				}[];
			};
		};
		Enums: {
			[_ in never]: never;
		};
		CompositeTypes: {
			[_ in never]: never;
		};
	};
}

export type Tables<T extends keyof Database['public']['Tables']> =
	Database['public']['Tables'][T]['Row'];
export type TablesInsert<T extends keyof Database['public']['Tables']> =
	Database['public']['Tables'][T]['Insert'];
export type TablesUpdate<T extends keyof Database['public']['Tables']> =
	Database['public']['Tables'][T]['Update'];
