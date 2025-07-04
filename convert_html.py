# -*- coding: utf-8 -*-
import os
import re
import argparse
from pathlib import Path
import html
import json
from datetime import datetime

# --- Icon and Style definitions ---
DIR_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-300" viewBox="0 0 20 20" fill="currentColor"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" /></svg>'
FILE_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-300" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" /></svg>'
ARROW_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>'
USER_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5 inline-block" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>'
CALENDAR_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5 inline-block" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" /></svg>'
SEARCH_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" /></svg>'


# --- HTML Template for Directories (New Themed Layout) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ptt2 精華區 {title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans TC', sans-serif; background-color: #e2e8f0; }} /* Slate 200 background */
    </style>
</head>
<body class="min-h-screen">
    <div class="p-8 sm:p-12 rounded-b-3xl bg-cover bg-center shadow-lg" style="background-image: url('https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=1920&auto=format&fit=crop');">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl md:text-5xl font-bold text-white tracking-tight [text-shadow:_0_2px_4px_rgb(0_0_0_/_40%)]">{title}</h1>
            {back_link}
        </div>
    </div>
    <main class="max-w-4xl mx-auto px-4 py-8">
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50">
            <div class="flex justify-end p-4 border-b border-gray-200/80">
                {search_link}
            </div>
            <div class="divide-y divide-gray-200/80">
                {content}
            </div>
        </div>
        <footer class="text-center mt-8 text-slate-500 text-sm">
            <p>2025/07/04/ Google Gemini 完成</p>
        </footer>
    </main>
</body>
</html>
"""

# --- HTML Template for Articles (New Fun Layout) ---
ARTICLE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article: {article_title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans TC', sans-serif; background-color: #1e293b; }} /* Slate 800 background */
        /* ANSI Color Styles */
        .ansi-bold {{ font-weight: bold; }}
        .ansi-black {{ color: #333; }} .ansi-bg-black {{ background-color: #333; }}
        .ansi-red {{ color: #ff5555; }} .ansi-bg-red {{ background-color: #ff5555; }}
        .ansi-green {{ color: #55ff55; }} .ansi-bg-green {{ background-color: #55ff55; }}
        .ansi-yellow {{ color: #ffff55; }} .ansi-bg-yellow {{ background-color: #ffff55; }}
        .ansi-blue {{ color: #5555ff; }} .ansi-bg-blue {{ background-color: #5555ff; }}
        .ansi-magenta {{ color: #ff55ff; }} .ansi-bg-magenta {{ background-color: #ff55ff; }}
        .ansi-cyan {{ color: #55ffff; }} .ansi-bg-cyan {{ background-color: #55ffff; }}
        .ansi-white {{ color: #ffffff; }} .ansi-bg-white {{ background-color: #ffffff; }}
        .ansi-bright-black {{ color: #888; }} .ansi-bg-bright-black {{ background-color: #888; }}
        .ansi-bright-red {{ color: #ff8888; }} .ansi-bg-bright-red {{ background-color: #ff8888; }}
        .ansi-bright-green {{ color: #88ff88; }} .ansi-bg-bright-green {{ background-color: #88ff88; }}
        .ansi-bright-yellow {{ color: #ffff88; }} .ansi-bg-bright-yellow {{ background-color: #ffff88; }}
        .ansi-bright-blue {{ color: #8888ff; }} .ansi-bg-bright-blue {{ background-color: #8888ff; }}
        .ansi-bright-magenta {{ color: #ff88ff; }} .ansi-bg-bright-magenta {{ background-color: #ff88ff; }}
        .ansi-bright-cyan {{ color: #88ffff; }} .ansi-bg-bright-cyan {{ background-color: #88ffff; }}
        .ansi-bright-white {{ color: #ffffff; }} .ansi-bg-bright-white {{ background-color: #ffffff; }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-5xl mx-auto">
        <div class="mb-6">
            <a href="index.html" class="text-indigo-400 hover:text-indigo-300 flex items-center space-x-2 text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                <span>Back to Directory</span>
            </a>
        </div>
        <div class="bg-slate-900 rounded-xl shadow-2xl overflow-hidden ring-1 ring-white/10">
            <div class="p-4 sm:p-5 border-b border-slate-700/50 flex items-center space-x-2">
                <div class="flex space-x-1.5">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
            </div>
            <div class="p-6 border-b border-slate-700/50">
                <h2 class="text-2xl font-bold text-white mb-3">{article_title}</h2>
                <div class="flex flex-wrap items-center text-sm text-slate-400 gap-x-4 gap-y-1">
                    <span class="flex items-center">{USER_ICON_SVG} {author}</span>
                    <span class="flex items-center">{CALENDAR_ICON_SVG} {date}</span>
                </div>
            </div>
            <div class="p-6 bg-black text-sm sm:text-base">
                <pre class="leading-relaxed" style="color: #cccccc;">{content}</pre>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- HTML Template for the Search Page ---
SEARCH_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用關鍵字搜尋</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans TC', sans-serif; background-color: #f1f5f9; }}
        .highlight {{ background-color: #a7f3d0; border-radius: 2px; }} /* Emerald 200 for highlights */
    </style>
</head>
<body class="p-4 sm:p-6 md:p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-slate-800 tracking-tight">關鍵字搜尋文章</h1>
            <p class="mt-2 text-slate-600">Search for articles and directories by keyword, author, or date (YYYY/MM/DD).</p>
        </header>

        <!-- Search Input -->
        <div class="relative mb-8">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                {SEARCH_ICON_SVG}
            </div>
            <input type="text" id="search-input" placeholder="Enter keywords to search..." class="block w-full pl-12 pr-4 py-4 text-lg border-gray-300 rounded-xl shadow-lg focus:ring-indigo-500 focus:border-indigo-500">
        </div>

        <!-- Results Area -->
        <div id="results-container" class="space-y-3">
            <p id="initial-message" class="text-center text-slate-500 py-10">Start typing to see search results.</p>
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('search-input');
        const resultsContainer = document.getElementById('results-container');
        const initialMessage = document.getElementById('initial-message');
        let searchIndex = [];

        // Fetch the search index
        async function loadSearchIndex() {{
            try {{
                const response = await fetch('search_index.json');
                searchIndex = await response.json();
                console.log(`Loaded ${{searchIndex.length}} items into search index.`);
            }} catch (error) {{
                console.error('Failed to load search index:', error);
                resultsContainer.innerHTML = '<p class="text-center text-red-500">Error: Could not load search_index.json</p>';
            }}
        }}

        function highlightText(text, query) {{
            if (!query || !text) return text;
            const escapedQuery = query.replace(/[-\/\\^$*+?.()|\[\]{{}}]/g, '\\\\$&');
            const regex = new RegExp(escapedQuery, 'gi');
            return text.replace(regex, (match) => `<span class="highlight">${{match}}</span>`);
        }}

        function displayResults(query) {{
            if (!query) {{
                resultsContainer.innerHTML = '';
                initialMessage.style.display = 'block';
                return;
            }}

            initialMessage.style.display = 'none';
            const lowerCaseQuery = query.toLowerCase();
            const results = searchIndex.filter(item => {{
                return (
                    item.title.toLowerCase().includes(lowerCaseQuery) ||
                    item.description.toLowerCase().includes(lowerCaseQuery) ||
                    item.author.toLowerCase().includes(lowerCaseQuery) ||
                    item.date.includes(query) || // Exact match for dates
                    (item.content && item.content.toLowerCase().includes(lowerCaseQuery))
                );
            }});

            if (results.length === 0) {{
                resultsContainer.innerHTML = '<p class="text-center text-slate-500 py-10">No results found.</p>';
                return;
            }}

            const resultsHTML = results.map(item => {{
                const icon = item.type === 'DIR' ? `{DIR_ICON_SVG}` : `{FILE_ICON_SVG}`;
                const title = highlightText(item.title, query);
                const description = highlightText(item.description, query);
                const author = highlightText(item.author, query);
                const date = highlightText(item.date, query);

                return `
                <a href="${{item.path}}" class="group block p-4 rounded-xl bg-white transition-all duration-200 hover:bg-white hover:shadow-lg hover:border-indigo-300 shadow-sm border border-gray-200">
                    <div class="flex items-center space-x-4">
                        <div class="flex-shrink-0 p-2 rounded-full ${{(item.type === 'DIR' ? 'bg-indigo-100' : 'bg-emerald-100')}}">${{icon}}</div>
                        <div class="flex-1 min-w-0">
                            <p class="text-base font-medium text-slate-800 truncate group-hover:text-indigo-600">${{title}}</p>
                            <p class="text-sm text-slate-500 truncate">${{description}}</p>
                        </div>
                        <div class="text-right text-xs text-slate-500 flex-shrink-0 w-24 space-y-1">
                            <p class="font-semibold text-slate-700">${{author}}</p>
                            <p>${{date}}</p>
                        </div>
                        <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">{ARROW_ICON_SVG}</div>
                    </div>
                </a>
                `;
            }}).join('');

            resultsContainer.innerHTML = resultsHTML;
        }}

        searchInput.addEventListener('input', (e) => {{
            displayResults(e.target.value);
        }});

        // Load the index when the page is ready
        document.addEventListener('DOMContentLoaded', loadSearchIndex);
    </script>
</body>
</html>
"""

def ansi_to_html(text):
    """
    Converts text with ANSI escape codes to HTML by processing the text as a stream.
    """
    fg_map = {
        '30': 'ansi-black', '31': 'ansi-red', '32': 'ansi-green', '33': 'ansi-yellow',
        '34': 'ansi-blue', '35': 'ansi-magenta', '36': 'ansi-cyan', '37': 'ansi-white',
        '90': 'ansi-bright-black', '91': 'ansi-bright-red', '92': 'ansi-bright-green', '93': 'ansi-bright-yellow',
        '94': 'ansi-bright-blue', '95': 'ansi-bright-magenta', '96': 'ansi-bright-cyan', '97': 'ansi-bright-white',
    }
    bg_map = {
        '40': 'ansi-bg-black', '41': 'ansi-bg-red', '42': 'ansi-bg-green', '43': 'ansi-bg-yellow',
        '44': 'ansi-bg-blue', '45': 'ansi-bg-magenta', '46': 'ansi-bg-cyan', '47': 'ansi-bg-white',
        '100': 'ansi-bg-bright-black', '101': 'ansi-bg-bright-red', '102': 'ansi-bg-bright-green', '103': 'ansi-bg-bright-yellow',
        '104': 'ansi-bg-bright-blue', '105': 'ansi-bg-bright-magenta', '106': 'ansi-bg-bright-cyan', '107': 'ansi-bg-bright-white',
    }
    parts = re.split(r'(\x1B\[[\d;]*m)', text)
    html_output, is_bold, fg_class, bg_class, is_reverse, span_is_open = [], False, None, None, False, False

    def close_span():
        nonlocal span_is_open
        if span_is_open:
            html_output.append('</span>')
            span_is_open = False

    def open_span():
        nonlocal span_is_open
        if span_is_open: close_span()
        classes = []
        current_fg, current_bg = fg_class, bg_class
        if is_reverse:
            current_fg, current_bg = current_bg, current_fg
            if current_fg and current_fg.startswith('ansi-bg-'): current_fg = current_fg.replace('bg-', '')
        if is_bold: classes.append('ansi-bold')
        if current_fg: classes.append(current_fg)
        if current_bg: classes.append(current_bg)
        if classes:
            html_output.append(f'<span class="{" ".join(classes)}">')
            span_is_open = True

    for part in parts:
        if not part: continue
        match = re.match(r'\x1B\[([\d;]*)m', part)
        if match:
            codes = match.group(1).split(';')
            if not codes or codes == [''] or codes == ['0']:
                close_span()
                is_bold, fg_class, bg_class, is_reverse = False, None, None, False
                continue
            for code in codes:
                if code == '1': is_bold = True
                elif code == '7': is_reverse = True
                elif code == '27': is_reverse = False
                elif code in fg_map: fg_class = fg_map[code]
                elif code in bg_map: bg_class = bg_map[code]
        else:
            open_span()
            html_output.append(html.escape(part))
    close_span()
    return "".join(html_output)

def parse_article_header(content):
    """
    Parses the header of a BBS article file to extract metadata.
    """
    author, title, date = 'N/A', 'N/A', 'N/A'
    for line in content.splitlines()[:5]:
        if line.startswith('作者'):
            match = re.search(r'作者:\s*(\S+)', line)
            if match: author = match.group(1)
        elif line.startswith('標題'):
            match = re.search(r'標題:\s*(.*)', line)
            if match: title = match.group(1).strip()
        elif line.startswith('時間'):
            match = re.search(r'時間:\s*(.*)', line)
            if match: date = match.group(1).strip()
    return {'author': author, 'title': title, 'date': date}

def strip_article_header(content):
    """
    Removes the Author/Title/Time header lines from the article body.
    """
    lines = content.splitlines()
    header_prefixes = ('作者:', '標題:', '時間:')
    
    # Find the index of the last header line
    last_header_index = -1
    for i, line in enumerate(lines[:5]): # Only check first 5 lines
        if line.strip().startswith(header_prefixes):
            last_header_index = i
            
    # If header lines were found, return the content after them, preserving initial newlines
    if last_header_index != -1:
        return '\n'.join(lines[last_header_index + 1:])
    
    return content

def parse_bbs_record(record_id, record_content, entry_path):
    """
    Parses a single data record from a .DIR file.
    """
    date_match = re.search(r'(\d{1,2}/\d{2})', record_content)
    year = ''
    try:
        if entry_path and entry_path.exists():
            mtime = entry_path.stat().st_mtime
            year = datetime.fromtimestamp(mtime).year
    except FileNotFoundError:
        pass

    if not date_match:
        if '精華區目錄索引' in record_content:
            desc = re.sub(r'[\x00-\x1F\^@]', ' ', record_content).strip().replace(record_id, '').strip()
            return {'id': record_id, 'date': str(year) if year else '', 'owner': '', 'description': desc}
        return None

    date = date_match.group(1)
    full_date = f"{year}/{date}" if year else date
    
    content_after_id = record_content[len(record_id):]
    before_date, after_date = content_after_id.split(date, 1)

    owner_text = re.sub(r'[\x00-\x1F\^@]', ' ', before_date).strip()
    owner_parts = owner_text.split()
    owner = owner_parts[-1] if owner_parts else ''

    clean_after_date = after_date.lstrip('\x00\^@\s◎—◆◇.')
    desc, *junk = clean_after_date.split('\x00', 1)
    desc = re.sub(r'\[[^\]]+\]\s*$', '', desc)
    if owner and len(owner) > 1 and desc.endswith(owner):
        desc = desc[:-len(owner)]
    
    description = desc.strip()

    return {'id': record_id, 'date': full_date, 'owner': owner, 'description': description}

def main():
    parser = argparse.ArgumentParser(description="Recursively convert BBS .DIR and article files to a navigable HTML structure.")
    parser.add_argument("source_dir", help="The source directory containing .DIR and article files.")
    parser.add_argument("output_dir", help="The directory where the mirrored HTML structure will be saved.")
    args = parser.parse_args()

    source_path = Path(args.source_dir).resolve()
    output_path = Path(args.output_dir)

    if not source_path.is_dir():
        print(f"Error: Source directory '{source_path}' not found.")
        return

    dir_files = list(source_path.glob('**/.DIR'))
    if not dir_files:
        print("No .DIR files found.")
        return

    search_data = []

    # --- Pre-scan Pass: Build a map of directory IDs to their names ---
    print("Pre-scanning to build directory name map...")
    dir_name_map = {}
    for file_path in dir_files:
        try:
            content_bytes = file_path.read_bytes()
            content_raw = content_bytes.decode('cp950', errors='ignore')
            id_regex = r'([A-Z][A-Z0-9]{2,3}|M\.[A-Z0-9\.]+)' 
            matches = list(re.finditer(id_regex, content_raw))

            for i, match in enumerate(matches):
                record_id = match.group(1)
                if record_id.startswith('D'):
                    start_pos = match.start()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content_raw)
                    record_content = content_raw[start_pos:end_pos]
                    parsed = parse_bbs_record(record_id, record_content, None)
                    if parsed and parsed.get('description'):
                        parts = re.split(r'\s{5,}', parsed['description'], 1)
                        title = parts[0]
                        dir_name_map[record_id] = title
        except Exception as e:
            print(f"Could not pre-scan file {file_path}: {e}")
            continue
    print("Name map built.")

    # --- Pass 1: Convert .DIR files ---
    print(f"Found {len(dir_files)} .DIR files. Processing directories...")
    for file_path in dir_files:
        try:
            content_bytes = file_path.read_bytes()
            content_raw = content_bytes.decode('cp950', errors='ignore').replace('^[[', '\x1B[')
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
            continue

        id_regex = r'([A-Z][A-Z0-9]{2,3}|M\.[A-Z0-9\.]+)'
        matches = list(re.finditer(id_regex, content_raw))
        
        card_html_items = []
        for i, match in enumerate(matches):
            record_id = match.group(1)
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content_raw)
            record_content = content_raw[start_pos:end_pos]
            
            is_directory = record_id.startswith('D')
            entry_path_in_source = file_path.parent / record_id
            if is_directory:
                entry_path_in_source = entry_path_in_source / '.DIR'

            parsed = parse_bbs_record(record_id, record_content, entry_path_in_source)
            if parsed and parsed.get('description'):
                parts = re.split(r'\s{5,}', parsed['description'], 1)
                if len(parts) > 1:
                    title, description = parts[0], parts[1]
                else:
                    title, description = parsed['description'], ''
                
                if is_directory:
                    link = f'{parsed["id"]}/index.html'
                    icon_svg = DIR_ICON_SVG
                    icon_bg = 'bg-indigo-100'
                    entry_type = 'DIR'
                else: # Is a file
                    link = f'{parsed["id"]}.html'
                    icon_svg = FILE_ICON_SVG
                    icon_bg = 'bg-emerald-100'
                    entry_type = 'File'
                
                # Add to search index
                relative_link = (file_path.parent / link).relative_to(source_path)
                search_data.append({
                    "title": title,
                    "description": description,
                    "author": parsed['owner'],
                    "date": parsed['date'],
                    "type": entry_type,
                    "path": str(relative_link).replace('\\', '/'),
                    "content": "" # Content will be added in Pass 2
                })
                
                card_html = f"""
                <a href="{link}" class="group block p-4 transition-all duration-200 hover:bg-indigo-50 hover:shadow-md hover:border-indigo-200 first:rounded-t-xl last:rounded-b-xl border-l-4 border-transparent hover:border-indigo-500">
                    <div class="flex items-center space-x-4">
                        <div class="flex-shrink-0 p-2 rounded-full {icon_bg}">
                            {icon_svg}
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-base font-medium text-slate-800 truncate group-hover:text-indigo-600">{title}</p>
                            <p class="text-sm text-slate-500 truncate">{description}</p>
                        </div>
                        <div class="text-right text-xs text-slate-500 flex-shrink-0 w-24 space-y-1">
                            <p class="font-semibold text-slate-700">{parsed['owner']}</p>
                            <p>{parsed['date']}</p>
                        </div>
                        <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                            {ARROW_ICON_SVG}
                        </div>
                    </div>
                </a>
                """
                card_html_items.append(card_html)
        
        parent_dir = file_path.parent
        relative_path_dir = parent_dir.relative_to(source_path)
        current_output_dir = output_path / relative_path_dir
        current_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file_path = current_output_dir / "index.html"
        
        if parent_dir == source_path:
            page_title = "Ｐtt2 精華區"
            search_link_html = f'<a href="search.html" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-white/20 hover:bg-white/30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-indigo-700 focus:ring-white">{SEARCH_ICON_SVG}<span class="ml-2">Search Archive</span></a>'
        else:
            dir_id = parent_dir.name
            page_title = dir_name_map.get(dir_id, dir_id)
            search_link_html = '' # No search button on subpages
        
        back_link_html = ''
        if parent_dir != source_path:
            grandparent_id = parent_dir.parent.name
            back_link_text = dir_name_map.get(grandparent_id, "root" if not grandparent_id else grandparent_id)
            back_link_html = f'<a href="../index.html" class="text-sm text-indigo-100 hover:text-white mt-2 inline-block flex items-center space-x-1"><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg><span>Back to {back_link_text}</span></a>'

        final_html = HTML_TEMPLATE.format(
            title=page_title,
            content="\n".join(card_html_items),
            back_link=back_link_html,
            search_link=search_link_html
        )
        output_file_path.write_text(final_html, encoding='utf-8')
        print(f"  -> Converted DIR '{file_path.relative_to(source_path)}' to '{output_file_path.relative_to(output_path)}'")

    # --- Pass 2: Convert article files and update search index ---
    all_files_in_source = [p for p in source_path.glob('**/*') if p.is_file() and p.name != '.DIR']
    if not all_files_in_source:
        print("\nNo article files found.")
    else:
        print(f"\nFound {len(all_files_in_source)} potential article files. Processing...")
        for article_path in all_files_in_source:
            try:
                article_content_bytes = article_path.read_bytes()
                article_content = article_content_bytes.decode('cp950', errors='ignore').replace('^[[', '\x1B[')
                
                header_data = parse_article_header(article_content)
                # Remove the header from the body content before converting to HTML
                body_content = strip_article_header(article_content)
                html_content = ansi_to_html(body_content)
                
                # Update the corresponding entry in the search index with the full content
                relative_link_str = str(article_path.relative_to(source_path)).replace('\\', '/') + ".html"
                for item in search_data:
                    if item['path'].endswith(relative_link_str):
                        item['content'] = article_content # Use original content for search index
                        item['author'] = header_data['author'] # Update with more accurate author if found
                        break

            except Exception as e:
                print(f"Could not read article file {article_path}: {e}")
                continue

            relative_path = article_path.relative_to(source_path)
            output_file_path = output_path / f"{relative_path}.html"
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

            final_html = ARTICLE_TEMPLATE.format(
                article_title=html.escape(header_data['title'] if header_data['title'] != 'N/A' else article_path.name),
                author=html.escape(header_data['author']),
                date=html.escape(header_data['date']),
                content=html_content,
                USER_ICON_SVG=USER_ICON_SVG,
                CALENDAR_ICON_SVG=CALENDAR_ICON_SVG
            )
            output_file_path.write_text(final_html, encoding='utf-8')
            print(f"  -> Converted Article '{article_path.relative_to(source_path)}' to '{output_file_path.relative_to(output_path)}'")

    # --- Pass 3: Write search index and search page ---
    print("\nGenerating search files...")
    # Save the search index JSON
    search_index_path = output_path / "search_index.json"
    with open(search_index_path, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False, indent=2)
    print(f"  -> Created search index at '{search_index_path.name}'")
    
    # Create the search HTML page
    search_page_path = output_path / "search.html"
    search_html = SEARCH_PAGE_TEMPLATE.format(
        SEARCH_ICON_SVG=SEARCH_ICON_SVG,
        DIR_ICON_SVG=DIR_ICON_SVG,
        FILE_ICON_SVG=FILE_ICON_SVG,
        ARROW_ICON_SVG=ARROW_ICON_SVG
    )
    search_page_path.write_text(search_html, encoding='utf-8')
    print(f"  -> Created search page at '{search_page_path.name}'")

    print("\nConversion complete!")
    print(f"HTML files saved in: {output_path.resolve()}")


if __name__ == "__main__":
    main()
