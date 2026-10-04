# 为 sub2study 贡献代码

[English](./CONTRIBUTING.md) · [简体中文](./CONTRIBUTING_zh.md)

感谢你对 **sub2study** 的关注与支持！我们非常欢迎各种形式的贡献，包括问题反馈、排版美化、多语种音标/重音方案扩展以及各类 AI Agent 规范的完善。

---

## 🛠 本地开发与环境准备

### 1. 基础依赖
- **Python 3.9+**
- **yt-dlp**（`brew install yt-dlp` 或 `pip install yt-dlp`）
- **Google Chrome / Chromium / Edge**（用于无头模式排版生成 PDF）

```bash
# 克隆代码仓库
git clone https://github.com/wanxiao2018/sub2study.git
cd sub2study

# 安装本地可编辑模式
pip install -e .
```

### 2. 运行与验证
```bash
# 测试字幕抓取与断句
sub2study extract "https://www.youtube.com/watch?v=vJwoB34Tv2U" -o ./test_output

# 测试讲义渲染与零碎文件自动归档
sub2study render ./test_output/bilingual_result.json -o ./test_output --title "测试讲义"
```

---

## 🤝 贡献流程 (Pull Request)

1. **Fork** 本仓库至个人 GitHub 账号；
2. 基于 `main` 分支拉取开发分支：`git checkout -b feature/your-feature-name`；
3. 遵循规范的代码风格，提交具有明确语义的 Commit 消息：
   - `feat:` 新增功能
   - `fix:` 修复缺陷
   - `docs:` 文档更新
   - `refactor:` 代码重构
4. 推送至个人远端：`git push origin feature/your-feature-name`；
5. 在 GitHub 发起 **Pull Request**，并详细描述改动点与测试情况。

---

## 📄 开源协议

所有提交至本项目的代码与文档均默认遵守 [MIT 开源许可证](./LICENSE)。
