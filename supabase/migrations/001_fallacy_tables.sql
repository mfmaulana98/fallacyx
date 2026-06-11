-- Migration: Create fallacy checker tables (analyses, vectors, feedback)
-- Saved to: supabase/migrations/001_fallacy_tables.sql

-- 1. ENUM FOR INPUT TYPE
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fallacy_input_type') THEN
        CREATE TYPE fallacy_input_type AS ENUM ('text', 'url', 'youtube', 'audio');
    END IF;
END$$;

-- 2. TABLE: fallacy_analyses
CREATE TABLE IF NOT EXISTS fallacy_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    input_type fallacy_input_type NOT NULL,
    input_content TEXT NOT NULL,
    input_title TEXT,
    transcript TEXT,
    fallacies_found JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_fallacies INTEGER DEFAULT 0,
    analysis_duration_ms INTEGER,
    model_used TEXT,
    is_public BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. TABLE: fallacy_vectors
CREATE TABLE IF NOT EXISTS fallacy_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES fallacy_analyses(id) ON DELETE CASCADE NOT NULL,
    fallacy_type TEXT NOT NULL,
    fallacy_text TEXT NOT NULL,
    embedding_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. TABLE: fallacy_feedback
CREATE TABLE IF NOT EXISTS fallacy_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES fallacy_analyses(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    fallacy_index INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_analysis_user_fallacy UNIQUE (analysis_id, user_id, fallacy_index)
);

-- 5. VIEW: public_analyses
CREATE OR REPLACE VIEW public_analyses AS
SELECT * FROM fallacy_analyses
WHERE is_public = true;

-- 6. INDEXES FOR QUERY PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_fallacy_analyses_user_id ON fallacy_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_fallacy_analyses_is_public ON fallacy_analyses(is_public);
CREATE INDEX IF NOT EXISTS idx_fallacy_vectors_analysis_id ON fallacy_vectors(analysis_id);
CREATE INDEX IF NOT EXISTS idx_fallacy_feedback_analysis_id ON fallacy_feedback(analysis_id);
CREATE INDEX IF NOT EXISTS idx_fallacy_feedback_user_id ON fallacy_feedback(user_id);

-- 7. TRIGGER FOR AUTO-UPDATE updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fallacy_analyses_updated_at ON fallacy_analyses;
CREATE TRIGGER trg_fallacy_analyses_updated_at
BEFORE UPDATE ON fallacy_analyses
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 8. FUNCTION & TRIGGER FOR AUTO-CALCULATE/INCREMENT total_fallacies FROM fallacies_found LENGTH
CREATE OR REPLACE FUNCTION calculate_total_fallacies()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fallacies_found IS NOT NULL THEN
        NEW.total_fallacies := jsonb_array_length(NEW.fallacies_found);
    ELSE
        NEW.total_fallacies := 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fallacy_analyses_total_fallacies ON fallacy_analyses;
CREATE TRIGGER trg_fallacy_analyses_total_fallacies
BEFORE INSERT OR UPDATE ON fallacy_analyses
FOR EACH ROW
EXECUTE FUNCTION calculate_total_fallacies();

-- Utility function to manually increment total_fallacies if needed
CREATE OR REPLACE FUNCTION increment_total_fallacies(p_analysis_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE fallacy_analyses
    SET total_fallacies = total_fallacies + 1,
        updated_at = now()
    WHERE id = p_analysis_id;
END;
$$ LANGUAGE plpgsql;

-- 9. ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE fallacy_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE fallacy_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE fallacy_feedback ENABLE ROW LEVEL SECURITY;

-- Policies for fallacy_analyses
DROP POLICY IF EXISTS "Users can read own analyses or public ones" ON fallacy_analyses;
CREATE POLICY "Users can read own analyses or public ones"
ON fallacy_analyses FOR SELECT
USING (auth.uid() = user_id OR is_public = true);

DROP POLICY IF EXISTS "Users can insert their own analyses" ON fallacy_analyses;
CREATE POLICY "Users can insert their own analyses"
ON fallacy_analyses FOR INSERT
WITH CHECK (auth.uid() = user_id OR user_id IS NULL); -- Allow anonymous analyses but associate with user if logged in

DROP POLICY IF EXISTS "Users can update their own analyses" ON fallacy_analyses;
CREATE POLICY "Users can update their own analyses"
ON fallacy_analyses FOR UPDATE
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own analyses" ON fallacy_analyses;
CREATE POLICY "Users can delete their own analyses"
ON fallacy_analyses FOR DELETE
USING (auth.uid() = user_id);

-- Policies for fallacy_vectors (derived from fallacy_analyses access)
DROP POLICY IF EXISTS "Users can read vectors of their own analyses or public ones" ON fallacy_vectors;
CREATE POLICY "Users can read vectors of their own analyses or public ones"
ON fallacy_vectors FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM fallacy_analyses
        WHERE fallacy_analyses.id = fallacy_vectors.analysis_id
        AND (fallacy_analyses.user_id = auth.uid() OR fallacy_analyses.is_public = true)
    )
);

DROP POLICY IF EXISTS "Users can insert vectors for their own analyses" ON fallacy_vectors;
CREATE POLICY "Users can insert vectors for their own analyses"
ON fallacy_vectors FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM fallacy_analyses
        WHERE fallacy_analyses.id = fallacy_vectors.analysis_id
        AND (fallacy_analyses.user_id = auth.uid() OR fallacy_analyses.user_id IS NULL)
    )
);

DROP POLICY IF EXISTS "Users can update vectors of their own analyses" ON fallacy_vectors;
CREATE POLICY "Users can update vectors of their own analyses"
ON fallacy_vectors FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM fallacy_analyses
        WHERE fallacy_analyses.id = fallacy_vectors.analysis_id
        AND fallacy_analyses.user_id = auth.uid()
    )
);

DROP POLICY IF EXISTS "Users can delete vectors of their own analyses" ON fallacy_vectors;
CREATE POLICY "Users can delete vectors of their own analyses"
ON fallacy_vectors FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM fallacy_analyses
        WHERE fallacy_analyses.id = fallacy_vectors.analysis_id
        AND fallacy_analyses.user_id = auth.uid()
    )
);

-- Policies for fallacy_feedback
DROP POLICY IF EXISTS "Users can read their own feedback or feedback on public analyses" ON fallacy_feedback;
CREATE POLICY "Users can read their own feedback or feedback on public analyses"
ON fallacy_feedback FOR SELECT
USING (
    auth.uid() = user_id
    OR EXISTS (
        SELECT 1 FROM fallacy_analyses
        WHERE fallacy_analyses.id = fallacy_feedback.analysis_id
        AND fallacy_analyses.is_public = true
    )
);

DROP POLICY IF EXISTS "Users can insert their own feedback" ON fallacy_feedback;
CREATE POLICY "Users can insert their own feedback"
ON fallacy_feedback FOR INSERT
WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Users can update their own feedback" ON fallacy_feedback;
CREATE POLICY "Users can update their own feedback"
ON fallacy_feedback FOR UPDATE
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own feedback" ON fallacy_feedback;
CREATE POLICY "Users can delete their own feedback"
ON fallacy_feedback FOR DELETE
USING (auth.uid() = user_id);
