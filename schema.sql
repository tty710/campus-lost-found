-- ???????? - Supabase ??? Schema
-- ? Supabase Dashboard > SQL Editor ??????

-- 1. ???
CREATE TABLE IF NOT EXISTS items (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(128) NOT NULL,
  description TEXT DEFAULT '',
  category VARCHAR(32) NOT NULL,
  location VARCHAR(128) DEFAULT '',
  found_date DATE NOT NULL,
  item_type VARCHAR(8) NOT NULL CHECK (item_type IN ('lost', 'found')),
  status VARCHAR(16) DEFAULT 'published',
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id);

-- 2. ???
CREATE TABLE IF NOT EXISTS images (
  id BIGSERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  filename VARCHAR(256) NOT NULL,
  url VARCHAR(512) DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_images_item_id ON images(item_id);

-- 3. ???
CREATE TABLE IF NOT EXISTS claims (
  id BIGSERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  claimant_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  message TEXT DEFAULT '',
  proof TEXT DEFAULT '',
  status VARCHAR(16) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'returned')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_claims_item_id ON claims(item_id);
CREATE INDEX IF NOT EXISTS idx_claims_claimant_id ON claims(claimant_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);

-- 4. RLS ??
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;

-- items: ?????
CREATE POLICY items_read ON items FOR SELECT USING (true);
-- items: ???????
CREATE POLICY items_insert ON items FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
-- items: ??????
CREATE POLICY items_update ON items FOR UPDATE USING (auth.uid() IS NOT NULL);
-- items: ??????  
CREATE POLICY items_delete ON items FOR DELETE USING (auth.uid() IS NOT NULL);

-- images: ?????
CREATE POLICY images_read ON images FOR SELECT USING (true);
CREATE POLICY images_insert ON images FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- claims: ?????
CREATE POLICY claims_read ON claims FOR SELECT USING (true);
CREATE POLICY claims_insert ON claims FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY claims_update ON claims FOR UPDATE USING (auth.uid() IS NOT NULL);
