# Contributing to sub2study

[English](./CONTRIBUTING.md) · [简体中文](./CONTRIBUTING_zh.md)

Thank you for your interest in contributing to **sub2study**! We welcome bug reports, typography improvements, new language profile presets, and AI agent integration enhancements.

---

## 🛠 Local Development Setup

### 1. Prerequisites
- **Python 3.9+**
- **yt-dlp** (`brew install yt-dlp` or `pip install yt-dlp`)
- **Google Chrome / Chromium / Edge** (for headless PDF compilation)

```bash
# Clone the repository
git clone https://github.com/wanxiao2018/sub2study.git
cd sub2study

# Setup development environment
pip install -e .
```

### 2. Testing CLI Commands
```bash
# Test extraction
sub2study extract "https://www.youtube.com/watch?v=vJwoB34Tv2U" -o ./test_output

# Test document rendering
sub2study render ./test_output/bilingual_result.json -o ./test_output --title "Test Title"
```

---

## 🤝 Contribution Workflow

1. **Fork** the repository;
2. Create a feature branch: `git checkout -b feature/my-feature`;
3. Commit your changes using semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`);
4. Push to your fork: `git push origin feature/my-feature`;
5. Submit a **Pull Request** explaining your motivation and changes.

---

## 📄 License

By contributing to sub2study, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
