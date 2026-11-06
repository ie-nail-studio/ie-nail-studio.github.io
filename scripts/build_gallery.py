#!/usr/bin/env python3
"""Generate static work cards from data/works.json; no third-party packages required."""
import argparse
from datetime import date, datetime
from zoneinfo import ZoneInfo
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('techniques', 'colors', 'effects', 'decorations', 'patterns', 'styles', 'campaigns')
BEGIN = '<!-- WORKS:START — 作品請編輯 data/works.json，再執行 scripts/build_gallery.py -->'
END = '<!-- WORKS:END -->'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_catalog():
    catalog = json.loads((ROOT / 'data/works.json').read_text(encoding='utf-8'))
    tags = json.loads((ROOT / 'data/tags.json').read_text(encoding='utf-8'))
    require(isinstance(tags, dict), 'tags.json 必須是標籤對照表')
    for tag, groups in tags.items():
        require(isinstance(tag, str) and tag and not tag.startswith('#'), '標籤不需加 #')
        require(isinstance(groups, dict) and groups, f'{tag} 缺少分類')
        for group, values in groups.items():
            require(group in GROUPS, f'{tag} 使用未知分類：{group}')
            require(isinstance(values, list) and values, f'{tag} 的分類值必須是清單')
            require(all(isinstance(v, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', v)
                        for v in values), f'{tag} 的 data 值格式錯誤')
    categories = {}
    for category in catalog['categories']:
        key = category['id']
        require(isinstance(key, str) and re.fullmatch(r'style-[a-z]+', key), '分類 id 格式錯誤')
        require(key not in categories, f'重複分類：{key}')
        require(isinstance(category['label'], str) and category['label'].strip(), f'{key} 缺少分類名稱')
        require(type(category['price']) is int and category['price'] >= 0, f'{key} 價格格式錯誤')
        require((ROOT / (key + '.html')).is_file(), f'找不到分類頁：{key}')
        categories[key] = category
    ids = set()
    orders = set()
    works = catalog['works']
    require(isinstance(works, list) and works, '作品清單不可為空')
    for work in works:
        key = work['id']
        require(isinstance(key, str) and re.fullmatch(r'[a-z0-9_-]+', key), '作品 id 格式錯誤')
        require(key not in ids, f'重複作品 id：{key}')
        ids.add(key)
        require(work['category'] in categories, f'{key} 使用未知分類')
        for field in ('image', 'name', 'alt'):
            require(isinstance(work[field], str) and work[field].strip(), f'{key} 缺少 {field}')
        image_path = Path(work['image'])
        require(not image_path.is_absolute() and image_path.parts[0] == 'img'
                and '..' not in image_path.parts, f'{key} 圖片必須位於 img 資料夾')
        require((ROOT / image_path).resolve().is_relative_to((ROOT / 'img').resolve()), f'{key} 圖片超出 img 資料夾')
        require((ROOT / image_path).is_file(), f'{key} 找不到圖片：{image_path}')
        require(isinstance(work.get('image_title', ''), str), f'{key} image_title 必須是文字')
        require(isinstance(work['tags'], list), f'{key} tags 必須是清單')
        require(all(isinstance(t, str) and t in tags for t in work['tags']), f'{key} 有未定義標籤，請先補 data/tags.json')
        require(len(set(work['tags'])) == len(work['tags']), f'{key} 標籤重複')
        require(type(work['sort_order']) is int and work['sort_order'] not in orders,
                f'{key} sort_order 必須是唯一整數')
        orders.add(work['sort_order'])
        published = work.get('published_date')
        require(isinstance(published, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', published),
                f'{key} 上架日期必須使用 YYYY-MM-DD 格式')
        try:
            date.fromisoformat(published)
        except ValueError:
            raise ValueError(f'{key} 上架日期不存在：{published}')
        offer = work.get('monthly_offer')
        require('本月限定' not in work['tags'], f'{key} 本月限定標籤由 monthly_offer 自動產生')
        if offer is not None:
            require(isinstance(offer, dict), f'{key} monthly_offer 必須是物件')
            month = offer.get('month')
            require(isinstance(month, str) and re.fullmatch(r'\d{4}-\d{2}', month), f'{key} 活動月份格式須為 YYYY-MM')
            date.fromisoformat(month + '-01')
            require(type(offer.get('price')) is int and 0 <= offer['price'] < categories[work['category']]['price'],
                    f'{key} 優惠價必須低於原價')
    return categories, sorted(works, key=lambda w: (-date.fromisoformat(w['published_date']).toordinal(), w['sort_order'])), tags


def data_attributes(work, tags):
    groups = {group: [] for group in GROUPS}
    for tag in work['tags']:
        for group, values in tags[tag].items():
            for value in values:
                if value not in groups[group]:
                    groups[group].append(value)
    return {group: ' '.join(values) for group, values in groups.items() if values}


def active_offer(work, as_of):
    offer = work.get('monthly_offer')
    return offer if offer and offer['month'] == as_of.strftime('%Y-%m') else None


def render_card(work, category, tags, index, as_of=None):
    esc = html.escape
    as_of = as_of or datetime.now(ZoneInfo('Asia/Taipei')).date()
    offer = active_offer(work, as_of)
    visible_tags = (['本月限定'] if offer else []) + work['tags']
    tagged_work = {**work, 'tags': visible_tags}
    attributes = {'work-id': work['id'], 'category': work['category'], 'published-date': work['published_date'], **data_attributes(tagged_work, tags)}
    attrs = ''.join(f'\n                         data-{key}="{esc(value, quote=True)}"'
                    for key, value in attributes.items())
    title = f' title="{esc(work["image_title"], quote=True)}"' if work.get('image_title') else ''
    tag_html = '\n'.join(f'                                <span class="tag">#{esc(tag)}</span>' for tag in visible_tags)
    badge = '\n                            <span class="badge-new">本月限定</span>' if offer else ''
    price_html = f"NT$ {category['price']:,}"
    if offer:
        price_html = (f'<span aria-label="優惠價">NT$ {offer["price"]:,}</span> '
                      f'<del class="original-price" aria-label="原價">NT$ {category["price"]:,}</del>')
    return f'''                    <!-- {esc(work['id'])} -->
                    <div class="nail-card"{attrs}>
                        <div class="nail-img-wrapper">{badge}
                            <img loading="{'eager' if index < 2 else 'lazy'}" decoding="async" src="{esc(work['image'], quote=True)}" alt="{esc(work['alt'], quote=True)}"{title}>
                        </div>
                        <div class="nail-info">
                            <h3>{esc(work['name'])}</h3>
                            <p class="price">{price_html}</p>
                            <div class="nail-tags">
{tag_html}
                            </div>
                        </div>
                    </div>'''


def replace_grid(source, cards):
    """Keep the existing page shell and replace only the balanced gallery-grid div."""
    openings = list(re.finditer(r'<div class="gallery-grid">', source))
    require(len(openings) == 1, '頁面必須剛好有一個 gallery-grid')
    opening = openings[0]
    depth = 1
    for token in re.finditer(r'<!--[\s\S]*?-->|<div\b[^>]*>|</div\s*>', source[opening.end():]):
        if token[0].startswith('<!--'):
            continue
        depth += -1 if token[0].startswith('</') else 1
        if depth == 0:
            end = opening.end() + token.start()
            return (source[:opening.end()] + '\n                    ' + BEGIN + '\n'
                    + '\n\n'.join(cards) + '\n                    ' + END
                    + '\n                ' + source[end:])
    raise ValueError('gallery-grid 缺少結尾標籤')


def generate(check=False, as_of=None):
    categories, works, tags = load_catalog()
    as_of = as_of or datetime.now(ZoneInfo('Asia/Taipei')).date()
    outputs = []
    for page in ['gallery', *categories, 'style-monthly']:
        if page == 'gallery':
            selected = works
        elif page == 'style-monthly':
            selected = [w for w in works if active_offer(w, as_of)]
        else:
            selected = [w for w in works if w['category'] == page]
        cards = [render_card(w, categories[w['category']], tags, i, as_of)
                 for i, w in enumerate(selected)]
        if page == 'style-monthly' and not cards:
            cards = ['                    <p>本月限定款準備中，歡迎透過 LINE 洽詢。</p>']
        path = ROOT / (page + '.html')
        source = path.read_text(encoding='utf-8')
        outputs.append((path, source, replace_grid(source, cards), len(selected)))
    # Validate every page before any output is written.
    changed = [path.name for path, before, after, _ in outputs if before != after]
    if check:
        require(not changed, '頁面尚未同步：' + ', '.join(changed))
        print(f'檢查通過：{len(works)} 張作品、{len(outputs)} 個頁面皆已同步。')
    else:
        for path, before, after, count in outputs:
            if before != after:
                path.write_text(after, encoding='utf-8')
            print(f'{path.name}：{count} 張作品')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只檢查資料和頁面是否同步，不修改檔案')
    args = parser.parse_args()
    try:
        generate(args.check)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f'未完成更新：{error}', file=sys.stderr)
        sys.exit(1)
