# Auto Green

This directory documents the daily empty-commit GitHub Actions automation for this repository.

该功能参考 [xueshanlinghu/auto-green](https://github.com/xueshanlinghu/auto-green) 的基本原理，使用 GitHub Actions 定时创建**空提交**，不改动任何项目文件。

## 配置

- 工作流：[`.github/workflows/auto-green.yml`](../.github/workflows/auto-green.yml)
- 仓库：`xihao-yang/Engineering-Project`
- 分支：`main`
- 计划：每天日本时间 09:17（UTC 00:17）
- 提交者：`Xihao Yang <249629196+xihao-yang@users.noreply.github.com>`
- 提交信息：`chore: daily activity check`
- 认证：GitHub Actions 自动提供的 `GITHUB_TOKEN`（无需创建个人访问令牌或 Secrets）

## 首次检查

1. 进入仓库的 **Actions** 标签页。
2. 选择左侧 **Auto Green**。
3. 点击 **Run workflow**，选择 `main`，确认运行。
4. 检查日志中是否有 `git commit --allow-empty` 和 `git push` 成功的信息。

GitHub 的定时任务可能延迟，极端情况下也可能跳过；不能保证每天准时执行。

## 暂停

在仓库 **Actions → Auto Green** 页面使用 **Disable workflow**，或者删除 `.github/workflows/auto-green.yml`。

## 注意

此工作流只生成空提交，不代表实际的软件开发活动。个人贡献图是否计入提交，仍由 GitHub 的贡献统计规则决定。
