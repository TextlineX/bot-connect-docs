#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import html2text
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://x2-aimdk.agibot.com/zh-cn/latest/"
SITE_PREFIX = "/zh-cn/latest/"
OFFICIAL_PREFIX = "/official"
OUTPUT_SUBDIR = "docs/official"
ASSET_SUBDIR = "_images"

PATH_PREFIX_MAP = {
    "about_agibot_X2/": "about/",
    "operation_guide/": "guide/",
    "quick_start/": "quickstart/",
    "Interface/": "interface/",
    "example/": "examples/",
    "faq/": "faq/",
    "get_sdk/": "get_sdk/",
}

EXAMPLE_SECTION_SLUGS = {
    "example/Python.html": {
        "py-get-mc-action": "robot-mode-get",
        "py-set-mc-action": "robot-mode-set",
        "py-preset-motion": "robot-action-set",
        "py-hand-control": "gripper",
        "py-omnihand-control": "hand",
        "py-set-mc-input-source": "input-register",
        "py-get-mc-input-source": "input-get",
        "py-locomotion": "locomotion",
        "py-motocontrol": "joint",
        "py-keyboard": "motion-keyboard",
        "py-take-photo": "camera-photo",
        "py-echo-cameras": "camera-stream",
        "py-echo-head-touch-sensor": "touch-sensor",
        "py-echo-lidar-data": "lidar",
        "py-play-video": "video-playback",
        "py-play-media": "media-playback",
        "py-play-tts": "tts",
        "py-mic-receiver": "microphone",
        "py-play-emoji": "emoji",
        "py-play-lights": "led",
    },
    "example/Cpp.html": {
        "cpp-get-mc-action": "robot-mode-get",
        "cpp-set-mc-action": "robot-mode-set",
        "cpp-preset-motion": "robot-action-set",
        "cpp-hand-control": "gripper",
        "cpp-omnihand-control": "hand",
        "cpp-set-mc-input-source": "input-register",
        "cpp-get-mc-input-source": "input-get",
        "cpp-locomotion": "locomotion",
        "cpp-motocontrol": "joint",
        "cpp-keyboard": "motion-keyboard",
        "cpp-take-photo": "camera-photo",
        "cpp-echo-cameras": "camera-stream",
        "cpp-echo-head-touch-sensor": "touch-sensor",
        "cpp-echo-lidar-data": "lidar",
        "cpp-play-video": "video-playback",
        "cpp-play-media": "media-playback",
        "cpp-play-tts": "tts",
        "cpp-mic-receiver": "microphone",
        "cpp-play-emoji": "emoji",
        "cpp-play-lights": "led",
    },
}


@dataclass(frozen=True)
class PageSpec:
    source_rel: str
    output_rel: str
    default_code_lang: str = ""


def build_page_spec(source_rel: str) -> PageSpec:
    clean = source_rel.strip("/")
    if clean in {"", "index.html"}:
        return PageSpec("index.html", "index.md")

    if clean == "example/Python.html":
        return PageSpec(clean, "examples/python/index.md", "python")

    if clean == "example/Cpp.html":
        return PageSpec(clean, "examples/cpp/index.md", "cpp")

    if clean == "example/index.html":
        return PageSpec(clean, "examples/index.md")

    if clean == "end_notes.html":
        return PageSpec(clean, "end_notes.md")

    if clean == "changelog.html":
        return PageSpec(clean, "changelog.md")

    if clean == "feedback.html":
        return PageSpec(clean, "feedback.md")

    for source_prefix, target_prefix in PATH_PREFIX_MAP.items():
        if clean.startswith(source_prefix):
            mapped = target_prefix + clean[len(source_prefix) :]
            return PageSpec(clean, mapped.removesuffix(".html") + ".md")

    raise ValueError(f"无法映射官方页面路径: {source_rel}")


def output_rel_to_vitepress_link(output_rel: str) -> str:
    if output_rel == "index.md":
        return f"{OFFICIAL_PREFIX}/"

    if output_rel.endswith("/index.md"):
        return f"{OFFICIAL_PREFIX}/{output_rel[:-9]}/"

    return f"{OFFICIAL_PREFIX}/{output_rel[:-3]}"


def official_url_to_local_link(
    absolute_url: str,
    example_anchor_routes: dict[tuple[str, str], str],
) -> str | None:
    parsed = urlparse(absolute_url)
    if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
        return None

    if not parsed.path.startswith(SITE_PREFIX):
        return None

    rel = parsed.path[len(SITE_PREFIX) :]
    try:
        spec = build_page_spec(rel)
    except ValueError:
        return None

    if parsed.fragment:
        example_link = example_anchor_routes.get((rel, parsed.fragment))
        if example_link is not None:
            return example_link

    link = output_rel_to_vitepress_link(spec.output_rel)
    if parsed.fragment:
        link = f"{link}#{parsed.fragment}"
    return link


def collect_source_pages(session: requests.Session) -> list[PageSpec]:
    response = session.get(urljoin(BASE_URL, "index.html"), timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    seen: set[str] = set()
    pages: list[PageSpec] = [build_page_spec("index.html")]

    selectors = [
        ".toctree-wrapper a.reference.internal[href]",
        ".wy-menu-vertical a[href]",
    ]

    for anchor in soup.select(", ".join(selectors)):
        href = anchor.get("href", "").strip()
        if not href:
            continue

        absolute = urljoin(BASE_URL, href)
        parsed = urlparse(absolute)
        if not parsed.path.startswith(SITE_PREFIX):
            continue

        rel = parsed.path[len(SITE_PREFIX) :]
        if not rel.endswith(".html"):
            continue

        if rel in seen or rel == "index.html":
            continue

        seen.add(rel)
        pages.append(build_page_spec(rel))

    return pages


def clean_generated_tree(output_root: Path) -> None:
    for name in [
        "about",
        "guide",
        "quickstart",
        "interface",
        "examples",
        "faq",
        "get_sdk",
        ASSET_SUBDIR,
        "end_notes.md",
        "changelog.md",
        "feedback.md",
        "index.md",
    ]:
        target = output_root / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def clean_heading_text(text: str) -> str:
    return re.sub(r"\s*\s*$", "", text).strip()


def clone_tag(tag: Tag) -> tuple[BeautifulSoup, Tag]:
    soup = BeautifulSoup(str(tag), "html.parser")
    root = next((node for node in soup.contents if isinstance(node, Tag)), None)
    if root is None:
        raise RuntimeError("HTML 片段克隆失败")
    return soup, root


def get_example_root_section(main: Tag) -> Tag:
    container = main.find("div", recursive=False) or main
    root_section = container.find("section", recursive=False) or container.find("section")
    if root_section is None:
        raise RuntimeError("示例页根 section 解析失败")
    return root_section


def iter_example_top_sections(root_section: Tag) -> list[Tag]:
    sections: list[Tag] = []
    for section in root_section.find_all("section", recursive=False):
        if section.find("h2", recursive=False):
            sections.append(section)
    return sections


def lower_heading_levels(root: Tag) -> None:
    mapping = {
        "h2": "h1",
        "h3": "h2",
        "h4": "h3",
        "h5": "h4",
        "h6": "h5",
    }
    for heading in root.find_all(list(mapping.keys())):
        heading.name = mapping[heading.name]


def build_example_anchor_routes(session: requests.Session) -> dict[tuple[str, str], str]:
    routes: dict[tuple[str, str], str] = {}

    for source_rel, slug_map in EXAMPLE_SECTION_SLUGS.items():
        page_url = urljoin(BASE_URL, source_rel)
        response = session.get(page_url, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        main = soup.select_one("[role='main']")
        if main is None:
            raise RuntimeError(f"示例页正文解析失败: {page_url}")

        root_section = get_example_root_section(main)
        spec = build_page_spec(source_rel)
        index_link = output_rel_to_vitepress_link(spec.output_rel)
        root_anchor = root_section.get("id", "").strip()
        if root_anchor:
            routes[(source_rel, root_anchor)] = index_link

        parent_dir = Path(spec.output_rel).parent.as_posix()
        for section in iter_example_top_sections(root_section):
            section_id = section.get("id", "").strip()
            if not section_id:
                continue

            slug = slug_map[section_id]
            file_link = f"{OFFICIAL_PREFIX}/{parent_dir}/{slug}"
            routes[(source_rel, section_id)] = file_link

            for element in section.select("[id]"):
                anchor_id = element.get("id", "").strip()
                if not anchor_id or anchor_id == section_id:
                    continue
                routes[(source_rel, anchor_id)] = f"{file_link}#{anchor_id}"

    return routes


def strip_code_line_numbers(pre: Tag) -> str:
    clone = BeautifulSoup(str(pre), "html.parser")
    pre_clone = clone.find("pre")
    if pre_clone is None:
        return ""

    for node in pre_clone.select("span.linenos"):
        node.decompose()

    code = pre_clone.get_text()
    return code.strip("\n")


def guess_code_language(block: Tag, default_lang: str) -> str:
    classes = block.get("class", [])
    class_text = " ".join(classes)

    if "highlight-bash" in class_text or "highlight-shell" in class_text:
        return "bash"
    if "highlight-cpp" in class_text or "highlight-c++" in class_text:
        return "cpp"
    if "highlight-python" in class_text:
        return "python"
    if "highlight-yaml" in class_text:
        return "yaml"
    if "highlight-json" in class_text:
        return "json"
    if "highlight-xml" in class_text:
        return "xml"
    if "highlight-cmake" in class_text:
        return "cmake"
    return default_lang


def replace_code_blocks(
    soup: BeautifulSoup,
    main: Tag,
    page_default_lang: str,
) -> list[tuple[str, str, str]]:
    code_blocks: list[tuple[str, str, str]] = []

    for block in list(main.select("div[class*='highlight-'].notranslate")):
        pre = block.select_one("pre")
        if pre is None:
            continue

        code = strip_code_line_numbers(pre)
        token = f"@@CODEBLOCK:{len(code_blocks)}@@"
        lang = guess_code_language(block, page_default_lang)
        code_blocks.append((token, lang, code))

        marker = soup.new_tag("p")
        marker.string = token
        block.replace_with(marker)

    return code_blocks


def inject_anchor_markers(soup: BeautifulSoup, main: Tag) -> None:
    seen: set[str] = set()

    for element in list(main.select("[id]")):
        anchor_id = element.get("id", "").strip()
        if not anchor_id or anchor_id in seen:
            continue

        seen.add(anchor_id)
        marker = soup.new_tag("p")
        marker.string = f"@@ANCHOR:{anchor_id}@@"
        element.insert_before(marker)


def unwrap_image_links(main: Tag) -> None:
    for anchor in list(main.select("a.image-reference")):
        images = anchor.find_all("img", recursive=False)
        if len(images) != 1 or anchor.get_text(strip=True):
            continue
        anchor.replace_with(images[0])


def download_asset(session: requests.Session, asset_url: str, asset_dir: Path) -> str:
    asset_dir.mkdir(parents=True, exist_ok=True)
    filename = urlparse(asset_url).path.rsplit("/", 1)[-1]
    destination = asset_dir / filename

    if not destination.exists():
        response = session.get(asset_url, timeout=30)
        response.raise_for_status()
        destination.write_bytes(response.content)

    return f"{OFFICIAL_PREFIX}/{ASSET_SUBDIR}/{filename}"


def rewrite_images(session: requests.Session, main: Tag, page_url: str, asset_dir: Path) -> None:
    for image in main.select("img[src]"):
        src = image.get("src", "").strip()
        if not src:
            continue
        absolute = urljoin(page_url, src)
        if urlparse(absolute).netloc != urlparse(BASE_URL).netloc:
            continue
        image["src"] = download_asset(session, absolute, asset_dir)


def rewrite_links(main: Tag, page_url: str) -> None:
    raise RuntimeError("rewrite_links 需要带 example_anchor_routes 参数调用")


def rewrite_links_with_routes(
    main: Tag,
    page_url: str,
    example_anchor_routes: dict[tuple[str, str], str],
) -> None:
    for anchor in main.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href:
            continue

        if href.startswith("#"):
            continue

        absolute = urljoin(page_url, href)
        mapped = official_url_to_local_link(absolute, example_anchor_routes)
        if mapped is not None:
            anchor["href"] = mapped


def normalize_page_fragment(main: Tag) -> None:
    for bad in main.select(".headerlink, .wy-breadcrumbs, .rst-footer-buttons, script, style"):
        bad.decompose()


def convert_html_to_markdown(main: Tag, code_blocks: Iterable[tuple[str, str, str]]) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = False
    converter.protect_links = True
    converter.single_line_break = False

    markdown = converter.handle(str(main))
    markdown = markdown.replace("", "")

    markdown = re.sub(
        r"(?m)^@@ANCHOR:([^@]+)@@$",
        lambda match: f'<a id="{match.group(1)}"></a>',
        markdown,
    )

    for token, lang, code in code_blocks:
        fence = f"```{lang}\n{code}\n```" if lang else f"```\n{code}\n```"
        markdown = markdown.replace(token, fence)

    markdown = re.sub(r"\]\(<([^>]+)>\)", r"](\1)", markdown)
    markdown = re.sub(r"\[\!\[(.*?)\]\((.*?)\)\s*\]\(<\2>\)", r"![\1](\2)", markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"
    return markdown


def render_fragment_markdown(
    session: requests.Session,
    soup: BeautifulSoup,
    fragment: Tag,
    page_url: str,
    asset_dir: Path,
    default_code_lang: str,
    example_anchor_routes: dict[tuple[str, str], str],
) -> str:
    normalize_page_fragment(fragment)
    unwrap_image_links(fragment)
    inject_anchor_markers(soup, fragment)
    rewrite_images(session, fragment, page_url, asset_dir)
    rewrite_links_with_routes(fragment, page_url, example_anchor_routes)
    code_blocks = replace_code_blocks(soup, fragment, default_code_lang)
    return convert_html_to_markdown(fragment, code_blocks)


def build_example_index_markdown(
    intro_markdown: str,
    links: list[tuple[str, str]],
) -> str:
    lines = [intro_markdown.rstrip(), "", "## 示例目录", ""]
    for title, href in links:
        lines.append(f"- [{title}]({href})")
    return "\n".join(lines).rstrip() + "\n"


def fetch_and_split_example_page(
    session: requests.Session,
    spec: PageSpec,
    output_root: Path,
    asset_dir: Path,
    example_anchor_routes: dict[tuple[str, str], str],
) -> list[Path]:
    page_url = urljoin(BASE_URL, spec.source_rel)
    response = session.get(page_url, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.select_one("[role='main']")
    if main is None:
        raise RuntimeError(f"页面正文解析失败: {page_url}")

    root_section = get_example_root_section(main)
    top_sections = iter_example_top_sections(root_section)
    slug_map = EXAMPLE_SECTION_SLUGS[spec.source_rel]
    section_links: list[tuple[str, str]] = []
    written_files: list[Path] = []

    intro_soup, intro_root = clone_tag(root_section)
    for nested in list(intro_root.find_all("section", recursive=False)):
        if nested.find("h2", recursive=False):
            nested.decompose()
    intro_markdown = render_fragment_markdown(
        session,
        intro_soup,
        intro_root,
        page_url,
        asset_dir,
        spec.default_code_lang,
        example_anchor_routes,
    )

    parent_dir = Path(spec.output_rel).parent
    for section in top_sections:
        section_id = section.get("id", "").strip()
        if not section_id:
            continue

        slug = slug_map[section_id]
        section_title = clean_heading_text(section.find("h2", recursive=False).get_text(" ", strip=True))
        section_links.append((section_title, f"{OFFICIAL_PREFIX}/{parent_dir.as_posix()}/{slug}"))

        section_soup, section_root = clone_tag(section)
        lower_heading_levels(section_root)
        section_markdown = render_fragment_markdown(
            session,
            section_soup,
            section_root,
            page_url,
            asset_dir,
            spec.default_code_lang,
            example_anchor_routes,
        )

        section_output = output_root / parent_dir / f"{slug}.md"
        section_output.parent.mkdir(parents=True, exist_ok=True)
        section_output.write_text(section_markdown, encoding="utf-8")
        written_files.append(section_output)

    index_output = output_root / spec.output_rel
    index_output.parent.mkdir(parents=True, exist_ok=True)
    index_output.write_text(build_example_index_markdown(intro_markdown, section_links), encoding="utf-8")
    written_files.insert(0, index_output)
    return written_files


def fetch_and_render_page(
    session: requests.Session,
    spec: PageSpec,
    output_root: Path,
    asset_dir: Path,
    example_anchor_routes: dict[tuple[str, str], str],
) -> list[Path]:
    if spec.source_rel in EXAMPLE_SECTION_SLUGS:
        return fetch_and_split_example_page(
            session,
            spec,
            output_root,
            asset_dir,
            example_anchor_routes,
        )

    page_url = urljoin(BASE_URL, spec.source_rel)
    response = session.get(page_url, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.select_one("[role='main']")
    if main is None:
        raise RuntimeError(f"页面正文解析失败: {page_url}")

    normalize_page_fragment(main)
    unwrap_image_links(main)
    inject_anchor_markers(soup, main)
    rewrite_images(session, main, page_url, asset_dir)
    rewrite_links_with_routes(main, page_url, example_anchor_routes)
    code_blocks = replace_code_blocks(soup, main, spec.default_code_lang)
    markdown = convert_html_to_markdown(main, code_blocks)

    output_path = output_root / spec.output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return [output_path]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="同步 AgiBot X2 官方文档到本地 docs/official")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="仓库根目录",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="保留现有 docs/official 内容，不在同步前清空",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root: Path = args.repo_root.resolve()
    output_root = repo_root / OUTPUT_SUBDIR
    asset_dir = output_root / ASSET_SUBDIR

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "bot-connect-doc-sync/1.0 (+https://x2-aimdk.agibot.com/)",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
    )

    example_anchor_routes = build_example_anchor_routes(session)
    pages = collect_source_pages(session)
    if not args.skip_clean:
        clean_generated_tree(output_root)

    written_files: list[Path] = []
    for spec in pages:
        written_files.extend(
            fetch_and_render_page(
                session,
                spec,
                output_root,
                asset_dir,
                example_anchor_routes,
            )
        )

    print(f"已同步页面: {len(written_files)}")
    print(f"图片目录: {asset_dir}")
    for path in written_files:
        print(path.relative_to(repo_root).as_posix())

    return 0


if __name__ == "__main__":
    sys.exit(main())
