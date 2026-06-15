-- ============================================
-- 校园失物招领平台 - 数据库初始化脚本
-- 在 Supabase SQL Editor 中运行
-- ============================================

-- 1. 用户资料表
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT NOT NULL UNIQUE,
  phone TEXT DEFAULT '',
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 物品表
CREATE TABLE IF NOT EXISTS items (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  category TEXT NOT NULL,
  location TEXT DEFAULT '',
  found_date DATE NOT NULL,
  item_type TEXT NOT NULL CHECK (item_type IN ('lost', 'found')),
  status TEXT DEFAULT 'published',
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 图片表
CREATE TABLE IF NOT EXISTS images (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  url TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 认领表
CREATE TABLE IF NOT EXISTS claims (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  claimant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  message TEXT DEFAULT '',
  proof TEXT DEFAULT '',
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- RLS 策略
-- ============================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read profiles" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

ALTER TABLE items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read items" ON items FOR SELECT USING (true);
CREATE POLICY "Users can create items" ON items FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own items" ON items FOR UPDATE USING (auth.uid() = user_id);

ALTER TABLE images ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read images" ON images FOR SELECT USING (true);
CREATE POLICY "Users can insert images" ON images FOR INSERT WITH CHECK (
  EXISTS (SELECT 1 FROM items WHERE items.id = item_id AND items.user_id = auth.uid())
);

ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read claims" ON claims FOR SELECT USING (true);
CREATE POLICY "Users can create claims" ON claims FOR INSERT WITH CHECK (auth.uid() = claimant_id);
CREATE POLICY "Owners can update claims" ON claims FOR UPDATE USING (
  EXISTS (SELECT 1 FROM items WHERE items.id = claims.item_id AND items.user_id = auth.uid())
  OR EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
);

-- ============================================
-- 自动创建 profile 的触发器
-- ============================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, username)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'username', NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
