# LightX2V Documentation

**English** | [中文](README_zh.md)

Online documentation for [LightX2V](https://github.com/ModelTC/LightX2V), covering setup, model usage, inference acceleration, and deployment. Built with MkDocs Material.

Online docs: [light-ai.top/LightX2V-Doc/](https://light-ai.top/LightX2V-Doc/)

## Local preview

Use a Python 3.11+ environment where you can install packages. LightX2V itself is not required.

```bash
git clone https://github.com/ModelTC/LightX2V-Doc.git
cd LightX2V-Doc

python -m pip install -r requirements.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/LightX2V-Doc/>. Use the language switch to choose Chinese or English.

The preview reloads when you edit the docs or theme. Press `Ctrl+C` to stop. For a remote preview, forward port `8000` to your local machine.

## Repository layout

| Path | Contents |
| --- | --- |
| [`docs/`](docs/) | Documentation content |
| [`mkdocs.yml`](mkdocs.yml) | Site and navigation settings |
| [`theme/`](theme/) | Theme, assets, and build scripts |
| [`requirements.txt`](requirements.txt) | Documentation build dependencies |
| [`.github/workflows/docs.yml`](.github/workflows/docs.yml) | Automated builds, checks, and deployment |

For editing, build checks, and publishing, see the [maintenance guide](MAINTAINING.md) (in Chinese).

## License

This project uses [Apache License 2.0](LICENSE). KaTeX uses [MIT](theme/assets/vendor/katex/LICENSE).
