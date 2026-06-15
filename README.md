# 校园失物招领平台

基于 **Supabase** + **GitHub Pages** 的全栈校园失物招领系统。

## 功能

- 失物/招领信息发布
- 图片上传（Supabase Storage）
- 分类搜索与关键词搜索
- 认领申请与审核
- 物品状态管理（发布→认领→归还）
- 管理员后台

## 技术栈

- **前端**: 原生 HTML/CSS/JS
- **后端/数据库**: Supabase (PostgreSQL + Auth + Storage)
- **部署**: GitHub Pages

## 部署步骤

### 1. Supabase 设置
1. 在 [Supabase SQL Editor](https://edagdtolpmspurnohxkw.supabase.com) 中运行 `schema.sql`
2. 在 Supabase Storage 中创建 `item-images` 公开存储桶
3. 在 Authentication → Settings 中启用 Email 登录

### 2. GitHub Pages
1. 进入仓库 Settings → Pages
2. Source 选择 `Deploy from a branch`
3. Branch 选择 `master`，目录选择 `/ (root)`
4. 保存后等待几分钟即可访问
