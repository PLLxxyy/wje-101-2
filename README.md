# 咖啡品鉴社区

咖啡品鉴社区是一个面向咖啡爱好者的全栈 Web 应用。用户可以记录品鉴笔记、维护冲煮配方、浏览豆种库，并通过点赞、评论和关注交流风味体验。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Element Plus、Pinia、Vue Router、Axios、ECharts
- 后端：Python 3.11、FastAPI、SQLAlchemy 2.0 async、Pydantic v2、python-jose、passlib
- 数据库：PostgreSQL 16
- 部署：Docker Compose、Nginx

## 快速启动

```bash
# 克隆项目
git clone <repo-url>
cd <project-dir>

# 配置环境变量
cp .env.example .env

# 一键启动
docker compose up -d --build

# 访问应用
# 前端：http://localhost:28601
# 后端 API 文档：http://localhost:29601/docs
```

## 端口说明

| 服务 | 容器端口 | 宿主机端口 |
|------|----------|------------|
| 前端（Nginx） | 80 | 28601 |
| 后端（FastAPI） | 8000 | 29601 |
| 数据库（PostgreSQL） | 5432 | 57601 |

## 预置账号

| 用户名 | 邮箱 | 密码 | 角色 |
|--------|------|------|------|
| barista_wang | wang@coffee.com | Coffee@2026 | 管理员 |
| coffee_lover | lover@coffee.com | Coffee@2026 | 普通用户 |
| bean_hunter | hunter@coffee.com | Coffee@2026 | 普通用户 |

## 项目结构

```text
frontend/
├── src/api
├── src/components/common
├── src/hooks
├── src/pages
├── src/router
├── src/stores
├── src/types
└── src/utils
backend/
├── app/config
├── app/controllers
├── app/middlewares
├── app/models
├── app/routes
├── app/services
├── app/types/schemas
└── app/utils
docker-compose.yml
.env.example
README.md
```

## API 概览

| 路由前缀 | 功能 |
|----------|------|
| /api/auth | 注册、登录、刷新 token |
| /api/users | 用户信息、关注/取关 |
| /api/notes | 品鉴笔记 CRUD、点赞 |
| /api/beans | 豆种管理 |
| /api/recipes | 冲煮配方 CRUD |
| /api/notes/:id/comments | 评论管理 |

## 本地验证命令

```bash
cd frontend
npm install
npm run typecheck
npm run build

cd ../backend
python -m py_compile $(find app -name "*.py")

cd ..
cp .env.example .env
docker compose config
docker compose up -d --build
docker compose ps
```

