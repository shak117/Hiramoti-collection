import re

files = [
    'index.html', 'about.html', 'founder.html', 'catalog.html',
    'gallery.html', 'contact.html', 'reels.html', 'privacy.html',
    'terms.html', 'shipping.html'
]

techno_dropdown = '''            <a href="collections.html?category=technosport" class="dropdown-link">
              <span>TechnoSport</span>
              <span class="dropdown-tag" style="background: rgba(220, 38, 38, 0.25); color: #fca5a5; font-weight: 700;">10% OFF</span>
            </a>
            <a href="collections.html?category=hosiery" class="dropdown-link">
              <span>Hosiery</span>
              <span class="dropdown-tag">Essentials</span>
            </a>'''

techno_drawer = '''          <a href="collections.html?category=technosport" class="drawer-sublink" style="color: #b91c1c; font-weight: 700;">• TechnoSport (10% OFF)</a>
          <a href="collections.html?category=hosiery" class="drawer-sublink">• Hosiery Essentials</a>'''

techno_footer = '''          <li><a href="collections.html?category=technosport">TechnoSport (10% OFF)</a></li>
          <li><a href="collections.html?category=hosiery">Hosiery</a></li>'''

for fname in files:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {fname}: {e}")
        continue

    # 1. Update nav-dropdown if technosport not in dropdown
    if 'category=technosport' not in content:
        # Match after Festive & Ethnic Wear link in dropdown
        pattern = r'(<a\s+href=["\']collections\.html\?category=ethnic["\'][^>]*>[\s\S]*?</a>\s*)(</div>\s*</div>)'
        if re.search(pattern, content):
            content = re.sub(pattern, r'\1' + techno_dropdown + '\n          ' + r'\2', content, count=1)
            print(f"Added dropdown to {fname}")
        else:
            print(f"Could not find ethnic dropdown link in {fname}")

    # 2. Update drawer-sublinks if technosport not in drawer
    drawer_marker = 'category=technosport'
    if drawer_marker not in content:
        drawer_pattern = r'(<a\s+href=["\']collections\.html\?category=ethnic["\'][^>]*class=["\']drawer-sublink["\'][^>]*>.*?</a>\s*)(</div>)'
        if re.search(drawer_pattern, content):
            content = re.sub(drawer_pattern, r'\1' + techno_drawer + '\n        ' + r'\2', content, count=1)
            print(f"Added drawer sublinks to {fname}")

    # 3. Update footer collections links
    footer_pattern = r'(<li><a\s+href=["\']collections\.html\?category=casual["\'][^>]*>.*?</a></li>\s*)'
    if 'category=technosport' not in content:
        if re.search(footer_pattern, content):
            content = re.sub(footer_pattern, r'\1' + techno_footer + '\n', content, count=1)
            print(f"Added footer links to {fname}")

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)

print("Batch navigation update complete!")
