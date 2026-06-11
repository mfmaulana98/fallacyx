-- Migration: Align fallacy_analyses, fallacy_feedback, user_fallacy_stats with the
-- updated FallacyX schema (input_hash/overall_severity, vote-based feedback,
-- current_streak/longest_streak naming) and add admin RLS overrides.
-- Saved to: supabase/migrations/20260611_fallacyx_schema.sql

-- ============================================================
-- 1. fallacy_analyses: rename + add columns
-- ============================================================
ALTER TABLE fallacy_analyses RENAME COLUMN fallacies_found TO fallacies;
ALTER TABLE fallacy_analyses RENAME COLUMN total_fallacies TO total_count;
ALTER TABLE fallacy_analyses RENAME COLUMN analysis_duration_ms TO processing_time_ms;
ALTER TABLE fallacy_analyses RENAME COLUMN model_used TO model_version;

ALTER TABLE fallacy_analyses
    ADD COLUMN IF NOT EXISTS input_hash TEXT,
    ADD COLUMN IF NOT EXISTS overall_severity TEXT;

CREATE INDEX IF NOT EXISTS idx_fallacy_analyses_input_hash ON fallacy_analyses(input_hash);
CREATE INDEX IF NOT EXISTS idx_fallacy_analyses_created_at ON fallacy_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fallacy_analyses_overall_severity ON fallacy_analyses(overall_severity);

-- ============================================================
-- 2. fallacy_feedback: replace is_correct boolean with vote text
-- ============================================================
ALTER TABLE fallacy_feedback ADD COLUMN IF NOT EXISTS vote TEXT;

UPDATE fallacy_feedback
SET vote = CASE WHEN is_correct THEN 'correct' ELSE 'incorrect' END
WHERE vote IS NULL;

ALTER TABLE fallacy_feedback ALTER COLUMN vote SET NOT NULL;
ALTER TABLE fallacy_feedback ADD CONSTRAINT fallacy_feedback_vote_check CHECK (vote IN ('correct', 'incorrect'));
ALTER TABLE fallacy_feedback DROP COLUMN is_correct;

-- ============================================================
-- 3. user_fallacy_stats: rename streak columns
-- ============================================================
ALTER TABLE user_fallacy_stats RENAME COLUMN streak_current TO current_streak;
ALTER TABLE user_fallacy_stats RENAME COLUMN streak_max TO longest_streak;

-- ============================================================
-- 4. calculate_total_fallacies: use renamed columns
-- ============================================================
CREATE OR REPLACE FUNCTION calculate_total_fallacies()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fallacies IS NOT NULL THEN
        NEW.total_count := jsonb_array_length(NEW.fallacies);
    ELSE
        NEW.total_count := 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 5. increment_analysis_stats: updates user_fallacy_stats after an
--    analysis is recorded (streak, totals, xp, level). Replaces update_streak.
-- ============================================================
DROP FUNCTION IF EXISTS update_streak(UUID);

CREATE OR REPLACE FUNCTION increment_analysis_stats(p_user_id UUID)
RETURNS VOID AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_last_date DATE;
    v_current_streak INT;
    v_longest_streak INT;
    v_fallacy_count INT;
    v_xp_gain INT;
BEGIN
    -- Fallacy count from the most recently recorded analysis for this user
    SELECT total_count INTO v_fallacy_count
    FROM fallacy_analyses
    WHERE user_id = p_user_id
    ORDER BY created_at DESC
    LIMIT 1;

    v_fallacy_count := COALESCE(v_fallacy_count, 0);
    v_xp_gain := 10 + (v_fallacy_count * 5);

    SELECT last_analysis_date, current_streak, longest_streak
    INTO v_last_date, v_current_streak, v_longest_streak
    FROM user_fallacy_stats
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO user_fallacy_stats (
            user_id, total_analyses, total_fallacies_found,
            current_streak, longest_streak, last_analysis_date,
            xp_points, level
        ) VALUES (
            p_user_id, 1, v_fallacy_count, 1, 1, v_today, v_xp_gain, 1 + FLOOR(v_xp_gain / 100.0)::INT
        );
        RETURN;
    END IF;

    IF v_last_date IS NULL OR v_last_date < v_today - INTERVAL '1 day' THEN
        v_current_streak := 1;
    ELSIF v_last_date = v_today - INTERVAL '1 day' THEN
        v_current_streak := v_current_streak + 1;
    END IF;
    -- If v_last_date = v_today, the streak is left unchanged.

    IF v_current_streak > v_longest_streak THEN
        v_longest_streak := v_current_streak;
    END IF;

    UPDATE user_fallacy_stats
    SET total_analyses = total_analyses + 1,
        total_fallacies_found = total_fallacies_found + v_fallacy_count,
        current_streak = v_current_streak,
        longest_streak = v_longest_streak,
        last_analysis_date = v_today,
        xp_points = xp_points + v_xp_gain,
        level = 1 + FLOOR((xp_points + v_xp_gain) / 100.0)::INT,
        updated_at = now()
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 6. check_and_award_achievements: use renamed longest_streak column
-- ============================================================
CREATE OR REPLACE FUNCTION check_and_award_achievements(p_user_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_analyses INT;
    v_total_fallacies INT;
    v_longest_streak INT;
    v_accuracy_score NUMERIC(5,2);
    v_has_ad_hominem BOOLEAN;
BEGIN
    SELECT total_analyses, total_fallacies_found, longest_streak, accuracy_score,
           COALESCE((fallacy_type_counts->>'ad_hominem')::INT, 0) > 0
    INTO v_total_analyses, v_total_fallacies, v_longest_streak, v_accuracy_score, v_has_ad_hominem
    FROM user_fallacy_stats
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    IF v_total_analyses >= 1 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'first_analysis', 5)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_longest_streak >= 3 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'streak_3', 10)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_longest_streak >= 7 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'streak_7', 20)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_total_fallacies >= 10 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'found_10_fallacies', 10)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_total_fallacies >= 100 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'found_100_fallacies', 50)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_has_ad_hominem THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'first_ad_hominem', 5)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    IF v_accuracy_score >= 90.00 AND EXISTS (
        SELECT 1 FROM fallacy_feedback
        WHERE user_id = p_user_id
        HAVING COUNT(*) >= 5
    ) THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'accuracy_90', 30)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 7. trg_after_analysis_insert_handler: use renamed columns and
--    delegate streak/xp/level bookkeeping to increment_analysis_stats
-- ============================================================
CREATE OR REPLACE FUNCTION trg_after_analysis_insert_handler()
RETURNS TRIGGER AS $$
DECLARE
    r RECORD;
    v_type TEXT;
    v_counts JSONB;
BEGIN
    IF NEW.user_id IS NOT NULL THEN
        PERFORM increment_analysis_stats(NEW.user_id);

        SELECT fallacy_type_counts INTO v_counts
        FROM user_fallacy_stats
        WHERE user_id = NEW.user_id;

        IF v_counts IS NULL THEN
            v_counts := '{}'::jsonb;
        END IF;

        FOR r IN SELECT jsonb_array_elements(NEW.fallacies) AS elem LOOP
            v_type := r.elem->>'type';
            IF v_type IS NOT NULL THEN
                v_counts := jsonb_set(
                    v_counts,
                    ARRAY[v_type],
                    to_jsonb(COALESCE((v_counts->>v_type)::INT, 0) + 1),
                    true
                );
            END IF;
        END LOOP;

        UPDATE user_fallacy_stats
        SET fallacy_type_counts = v_counts
        WHERE user_id = NEW.user_id;

        PERFORM check_and_award_achievements(NEW.user_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 8. update_user_accuracy_score: derive accuracy from vote = 'correct'
-- ============================================================
CREATE OR REPLACE FUNCTION update_user_accuracy_score()
RETURNS TRIGGER AS $$
DECLARE
    v_author_id UUID;
    v_new_accuracy NUMERIC(5,2);
    v_analysis_id UUID;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_analysis_id := OLD.analysis_id;
    ELSE
        v_analysis_id := NEW.analysis_id;
    END IF;

    SELECT user_id INTO v_author_id
    FROM fallacy_analyses
    WHERE id = v_analysis_id;

    IF v_author_id IS NOT NULL THEN
        SELECT
            COALESCE(
                (COUNT(CASE WHEN f.vote = 'correct' THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC) * 100.00,
                0.00
            )
        INTO v_new_accuracy
        FROM fallacy_feedback f
        JOIN fallacy_analyses a ON f.analysis_id = a.id
        WHERE a.user_id = v_author_id;

        UPDATE user_fallacy_stats
        SET accuracy_score = v_new_accuracy,
            updated_at = now()
        WHERE user_id = v_author_id;

        PERFORM check_and_award_achievements(v_author_id);
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 9. get_leaderboard: rename streak_max -> longest_streak in output
-- ============================================================
DROP FUNCTION IF EXISTS get_leaderboard(INT);

CREATE OR REPLACE FUNCTION get_leaderboard(p_limit INT DEFAULT 20)
RETURNS TABLE (
    user_id UUID,
    username TEXT,
    avatar_url TEXT,
    total_analyses INT,
    total_fallacies_found INT,
    longest_streak INT,
    level INT,
    xp_points INT,
    accuracy_score NUMERIC(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.user_id,
        p.username::TEXT,
        p.avatar_url::TEXT,
        s.total_analyses,
        s.total_fallacies_found,
        s.longest_streak,
        s.level,
        s.xp_points,
        s.accuracy_score
    FROM user_fallacy_stats s
    LEFT JOIN profiles p ON s.user_id = p.id
    ORDER BY s.xp_points DESC, s.total_analyses DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 10. Admin RLS overrides
-- ============================================================
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false;

CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_is_admin BOOLEAN;
BEGIN
    SELECT COALESCE(profiles.is_admin, false) INTO v_is_admin
    FROM profiles
    WHERE profiles.id = auth.uid();

    RETURN COALESCE(v_is_admin, false);
END;
$$;

DROP POLICY IF EXISTS "Admins can manage all analyses" ON fallacy_analyses;
CREATE POLICY "Admins can manage all analyses"
ON fallacy_analyses FOR ALL
USING (is_admin())
WITH CHECK (is_admin());

DROP POLICY IF EXISTS "Admins can manage all feedback" ON fallacy_feedback;
CREATE POLICY "Admins can manage all feedback"
ON fallacy_feedback FOR ALL
USING (is_admin())
WITH CHECK (is_admin());

DROP POLICY IF EXISTS "Admins can manage all stats" ON user_fallacy_stats;
CREATE POLICY "Admins can manage all stats"
ON user_fallacy_stats FOR ALL
USING (is_admin())
WITH CHECK (is_admin());
