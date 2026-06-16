// Supabase 配置
const SUPABASE_URL = 'https://edagdtolpmspurnohxkw.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_U1ZxM-iEhXxPH4imV2g2AA_Lvqpsri9';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

function formatDate(d) { if(!d) return ''; return new Date(d).toLocaleDateString('zh-CN'); }
function getStatusText(s) { const m={published:'发布中',claimed:'已认领',returned:'已归还',closed:'已关闭'}; return m[s]||s; }
function getTypeBadge(t) { return t==='lost'?'<span class="badge badge-lost">寻物</span>':'<span class="badge badge-found">招领</span>'; }

async function checkAuth() { const {data:{session}}=await supabase.auth.getSession(); return session; }

async function getProfile() {
  const {data:{session}} = await supabase.auth.getSession();
  if (!session) return null;
  const {data} = await supabase.from('profiles').select('*').eq('id', session.user.id).single();
  if (data) return data;
  // 没有 profile？自动创建一个
  const username = session.user.user_metadata?.username || session.user.email;
  const phone = session.user.user_metadata?.phone || '';
  const {data: newProfile, error} = await supabase.from('profiles').insert({
    id: session.user.id, username: username, phone: phone
  }).select().single();
  if (error) {
    console.error('Auto-create profile failed:', error);
    return null;
  }
  return newProfile;
}

async function logout() { await supabase.auth.signOut(); window.location.href='index.html'; }

async function updateNav() {
  const session = await checkAuth();
  const navEl = document.getElementById('nav-user');
  if (!navEl) return;
  if (session) {
    const profile = await getProfile();
    const isAdmin = profile && profile.role === 'admin';
    navEl.innerHTML = '<span style="margin-right:12px;">欢迎，'+(profile?profile.username:session.user.email)+'</span>'+
      (isAdmin?'<a href="admin.html" class="btn btn-outline">管理</a>':'')+
      '<a href="post.html" class="btn btn-primary">发布信息</a> '+
      '<a href="#" onclick="logout();return false;" class="btn btn-outline">退出</a>';
  } else {
    navEl.innerHTML = '<a href="auth.html" class="btn btn-primary">登录/注册</a>';
  }
}
