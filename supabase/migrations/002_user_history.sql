-- Migration: Create user fallacy history, stats, achievements, and challenges tables
-- Saved to: supabase/migrations/002_user_history.sql

-- 1. TABLE: user_fallacy_stats
CREATE TABLE IF NOT EXISTS user_fallacy_stats (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    total_analyses INTEGER DEFAULT 0,
    total_fallacies_found INTEGER DEFAULT 0,
    streak_current INTEGER DEFAULT 0,
    streak_max INTEGER DEFAULT 0,
    last_analysis_date DATE,
    fallacy_type_counts JSONB DEFAULT '{}'::jsonb,
    accuracy_score NUMERIC(5,2) DEFAULT 0.00,
    level INTEGER DEFAULT 1,
    xp_points INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. TABLE: fallacy_achievements
CREATE TABLE IF NOT EXISTS fallacy_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    achievement_code TEXT NOT NULL,
    unlocked_at TIMESTAMPTZ DEFAULT now(),
    diamond_reward INTEGER DEFAULT 0,
    CONSTRAINT unique_user_achievement UNIQUE (user_id, achievement_code)
);

-- 3. TABLE: daily_fallacy_challenges
CREATE TABLE IF NOT EXISTS daily_fallacy_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_date DATE NOT NULL UNIQUE,
    content_url TEXT NOT NULL,
    content_type TEXT NOT NULL,
    expected_fallacy_types TEXT[] NOT NULL,
    diamond_reward INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. TABLE: daily_challenge_submissions
CREATE TABLE IF NOT EXISTS daily_challenge_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    challenge_id UUID REFERENCES daily_fallacy_challenges(id) ON DELETE CASCADE NOT NULL,
    analysis_id UUID REFERENCES fallacy_analyses(id) ON DELETE CASCADE NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_user_challenge UNIQUE (user_id, challenge_id)
);

-- 5. INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_user_fallacy_stats_xp ON user_fallacy_stats(xp_points DESC);
CREATE INDEX IF NOT EXISTS idx_fallacy_achievements_user ON fallacy_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_challenge_submissions_user ON daily_challenge_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_challenge_submissions_challenge ON daily_challenge_submissions(challenge_id);

-- 6. TRIGGER FOR AUTO-UPDATE updated_at ON user_fallacy_stats
-- (Reuses the update_updated_at_column function if it exists; otherwise creates it)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_fallacy_stats_updated_at ON user_fallacy_stats;
CREATE TRIGGER trg_user_fallacy_stats_updated_at
BEFORE UPDATE ON user_fallacy_stats
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 7. FUNCTION: update_streak
CREATE OR REPLACE FUNCTION update_streak(p_user_id UUID)
RETURNS VOID AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_last_date DATE;
    v_current_streak INT;
    v_max_streak INT;
BEGIN
    -- Fetch existing stats
    SELECT last_analysis_date, streak_current, streak_max
    INTO v_last_date, v_current_streak, v_max_streak
    FROM user_fallacy_stats
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        -- Initialize stats record if it doesn't exist yet
        INSERT INTO user_fallacy_stats (
            user_id,
            total_analyses,
            total_fallacies_found,
            streak_current,
            streak_max,
            last_analysis_date
        ) VALUES (
            p_user_id,
            0,
            0,
            1,
            1,
            v_today
        );
        RETURN;
    END IF;

    -- Evaluate streak logic
    IF v_last_date IS NULL THEN
        v_current_streak := 1;
    ELSIF v_last_date = v_today THEN
        -- Already completed an analysis today; streak remains unchanged
        RETURN;
    ELSIF v_last_date = v_today - INTERVAL '1 day' THEN
        -- Successive day analysis; increment streak
        v_current_streak := v_current_streak + 1;
    ELSE
        -- Days missed; streak resets to 1
        v_current_streak := 1;
    END IF;

    -- Update maximum streak record if beaten
    IF v_current_streak > v_max_streak THEN
        v_max_streak := v_current_streak;
    END IF;

    -- Save updated streak info
    UPDATE user_fallacy_stats
    SET streak_current = v_current_streak,
        streak_max = v_max_streak,
        last_analysis_date = v_today,
        updated_at = now()
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- 8. FUNCTION: check_and_award_achievements
CREATE OR REPLACE FUNCTION check_and_award_achievements(p_user_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_analyses INT;
    v_total_fallacies INT;
    v_streak_max INT;
    v_accuracy_score NUMERIC(5,2);
    v_has_ad_hominem BOOLEAN;
BEGIN
    -- Fetch current statistics
    SELECT total_analyses, total_fallacies_found, streak_max, accuracy_score,
           COALESCE((fallacy_type_counts->>'ad_hominem')::INT, 0) > 0
    INTO v_total_analyses, v_total_fallacies, v_streak_max, v_accuracy_score, v_has_ad_hominem
    FROM user_fallacy_stats
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    -- Award 'first_analysis'
    IF v_total_analyses >= 1 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'first_analysis', 5)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'streak_3'
    IF v_streak_max >= 3 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'streak_3', 10)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'streak_7'
    IF v_streak_max >= 7 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'streak_7', 20)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'found_10_fallacies'
    IF v_total_fallacies >= 10 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'found_10_fallacies', 10)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'found_100_fallacies'
    IF v_total_fallacies >= 100 THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'found_100_fallacies', 50)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'first_ad_hominem'
    IF v_has_ad_hominem THEN
        INSERT INTO fallacy_achievements (user_id, achievement_code, diamond_reward)
        VALUES (p_user_id, 'first_ad_hominem', 5)
        ON CONFLICT (user_id, achievement_code) DO NOTHING;
    END IF;

    -- Award 'accuracy_90' (min 5 community reviews)
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

-- 9. TRIGGER HANDLER: Update stats after an analysis is inserted
CREATE OR REPLACE FUNCTION trg_after_analysis_insert_handler()
RETURNS TRIGGER AS $$
DECLARE
    r RECORD;
    v_type TEXT;
    v_counts JSONB;
BEGIN
    IF NEW.user_id IS NOT NULL THEN
        -- 1. Ensure user stats row is initialized / update streak
        PERFORM update_streak(NEW.user_id);
        
        -- 2. Fetch current fallacy type counts
        SELECT fallacy_type_counts INTO v_counts
        FROM user_fallacy_stats
        WHERE user_id = NEW.user_id;

        IF v_counts IS NULL THEN
            v_counts := '{}'::jsonb;
        END IF;

        -- 3. Accumulate counts for each fallacy type detected
        FOR r IN SELECT jsonb_array_elements(NEW.fallacies_found) AS elem LOOP
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

        -- 4. Update stats, XP, and Level (Formula: 10 XP base + 5 XP per fallacy, Level up every 100 XP)
        UPDATE user_fallacy_stats
        SET total_analyses = total_analyses + 1,
            total_fallacies_found = total_fallacies_found + NEW.total_fallacies,
            fallacy_type_counts = v_counts,
            xp_points = xp_points + 10 + (NEW.total_fallacies * 5),
            level = 1 + FLOOR((xp_points + 10 + (NEW.total_fallacies * 5)) / 100)::INT,
            updated_at = now()
        WHERE user_id = NEW.user_id;

        -- 5. Trigger checks for achievements
        PERFORM check_and_award_achievements(NEW.user_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Bind trigger to fallacy_analyses
DROP TRIGGER IF EXISTS trg_after_fallacy_analysis_insert ON fallacy_analyses;
CREATE TRIGGER trg_after_fallacy_analysis_insert
AFTER INSERT ON fallacy_analyses
FOR EACH ROW
EXECUTE FUNCTION trg_after_analysis_insert_handler();

-- 10. TRIGGER HANDLER: Recalculate accuracy score on user feedback events
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

    -- Fetch the author of the analysis
    SELECT user_id INTO v_author_id
    FROM fallacy_analyses
    WHERE id = v_analysis_id;

    IF v_author_id IS NOT NULL THEN
        -- Calculate percentage of positive feedback submissions
        SELECT 
            COALESCE(
                (COUNT(CASE WHEN f.is_correct THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC) * 100.00,
                0.00
            )
        INTO v_new_accuracy
        FROM fallacy_feedback f
        JOIN fallacy_analyses a ON f.analysis_id = a.id
        WHERE a.user_id = v_author_id;

        -- Update stats
        UPDATE user_fallacy_stats
        SET accuracy_score = v_new_accuracy,
            updated_at = now()
        WHERE user_id = v_author_id;

        -- Re-evaluate accuracy-related achievements
        PERFORM check_and_award_achievements(v_author_id);
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Bind trigger to fallacy_feedback
DROP TRIGGER IF EXISTS trg_fallacy_feedback_accuracy ON fallacy_feedback;
CREATE TRIGGER trg_fallacy_feedback_accuracy
AFTER INSERT OR UPDATE OR DELETE ON fallacy_feedback
FOR EACH ROW
EXECUTE FUNCTION update_user_accuracy_score();

-- 11. FUNCTION: get_leaderboard
CREATE OR REPLACE FUNCTION get_leaderboard(p_limit INT DEFAULT 20)
RETURNS TABLE (
    user_id UUID,
    username TEXT,
    avatar_url TEXT,
    total_analyses INT,
    total_fallacies_found INT,
    streak_max INT,
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
        s.streak_max,
        s.level,
        s.xp_points,
        s.accuracy_score
    FROM user_fallacy_stats s
    LEFT JOIN profiles p ON s.user_id = p.id
    ORDER BY s.xp_points DESC, s.total_analyses DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 12. ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE user_fallacy_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE fallacy_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_fallacy_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_challenge_submissions ENABLE ROW LEVEL SECURITY;

-- Policies for user_fallacy_stats
DROP POLICY IF EXISTS "Public can view all user stats" ON user_fallacy_stats;
CREATE POLICY "Public can view all user stats"
ON user_fallacy_stats FOR SELECT
USING (true); -- Publicly viewable for leaderboard functionality

DROP POLICY IF EXISTS "Users can only insert own stats" ON user_fallacy_stats;
CREATE POLICY "Users can only insert own stats"
ON user_fallacy_stats FOR INSERT
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only update own stats" ON user_fallacy_stats;
CREATE POLICY "Users can only update own stats"
ON user_fallacy_stats FOR UPDATE
USING (auth.uid() = user_id);

-- Policies for fallacy_achievements
DROP POLICY IF EXISTS "Public can view all achievements" ON fallacy_achievements;
CREATE POLICY "Public can view all achievements"
ON fallacy_achievements FOR SELECT
USING (true); -- Unlocked achievements can be seen by everyone (e.g. for user profile displays)

-- Write policies for fallacy_achievements are omitted, blocking direct user inserts/updates.
-- Updates can only occur through security definer triggers or service role.

-- Policies for daily_fallacy_challenges
DROP POLICY IF EXISTS "Public can view daily challenges" ON daily_fallacy_challenges;
CREATE POLICY "Public can view daily challenges"
ON daily_fallacy_challenges FOR SELECT
USING (true); -- Everyone can view challenges

-- Write policies for daily_fallacy_challenges are omitted. Only admin/service role can manage challenges.

-- Policies for daily_challenge_submissions
DROP POLICY IF EXISTS "Users can view own submissions" ON daily_challenge_submissions;
CREATE POLICY "Users can view own submissions"
ON daily_challenge_submissions FOR SELECT
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own submissions" ON daily_challenge_submissions;
CREATE POLICY "Users can insert own submissions"
ON daily_challenge_submissions FOR INSERT
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own submissions" ON daily_challenge_submissions;
CREATE POLICY "Users can update own submissions"
ON daily_challenge_submissions FOR UPDATE
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own submissions" ON daily_challenge_submissions;
CREATE POLICY "Users can delete own submissions"
ON daily_challenge_submissions FOR DELETE
USING (auth.uid() = user_id);
