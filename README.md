# Bot Connect 文档站

本目录使用 [VitePress](https://vitepress.dev/) 构建，托管于 Cloudflare Pages。

## 本地开发

```bash
cd docs
npm install
npm run dev
```

## 构建

```bash
npm run build
```

构建产物输出到 `.vitepress/dist/`。

## 部署

推送到 GitHub 后，Cloudflare Pages 自动构建并部署。

## 目录结构

```
docs/
├── index.md              首页
├── project/              项目文档（架构/部署/启动/动作）
├── setup/                环境搭建指南
├── sensors/             传感器硬件抽象层
├── development/         开发规范
├── slam/                SLAM 算法
└── official/            官方文档导览
```
