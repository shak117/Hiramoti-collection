import os

pages = ["about.html", "catalog.html", "collections.html", "contact.html", "founder.html", "gallery.html", "reels.html"]

for page in pages:
    with open(page, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Satara Heritage column
    if page == "founder.html":
        target1 = '<li><a href="https://www.instagram.com/hiramoticollection/" target="_blank" rel="noopener">Instagram @hiramoticollection</a></li>\n        </ul>'
        repl1 = '<li><a href="https://www.instagram.com/hiramoticollection/" target="_blank" rel="noopener">Instagram @hiramoticollection</a></li>\n          <li><a href="admin/index.html?role=admin" class="footer-admin-link">Admin Portal</a></li>\n          <li><a href="admin/index.html?role=super_admin" class="footer-superadmin-link">Super Admin</a></li>\n        </ul>'
    else:
        target1 = '<li><a href="contact.html#faq">Shopping FAQs</a></li>\n        </ul>'
        repl1 = '<li><a href="contact.html#faq">Shopping FAQs</a></li>\n          <li><a href="admin/index.html?role=admin" class="footer-admin-link">Admin Portal</a></li>\n          <li><a href="admin/index.html?role=super_admin" class="footer-superadmin-link">Super Admin</a></li>\n        </ul>'

    # 2. Update footer-bottom-links
    target2 = '<a href="contact.html">Store Map</a>\n        </div>'
    repl2 = '<a href="contact.html">Store Map</a>\n          <span>•</span>\n          <a href="admin/index.html?role=admin" class="footer-admin-link" title="Store Admin Portal">Admin</a>\n          <span>•</span>\n          <a href="admin/index.html?role=super_admin" class="footer-superadmin-link" title="Super Admin Portal">Super Admin</a>\n        </div>'

    if target1 in content:
        content = content.replace(target1, repl1, 1)
        print(f"[{page}] Replaced Satara Heritage links")
    else:
        print(f"[{page}] WARNING: Target 1 not found")

    if target2 in content:
        content = content.replace(target2, repl2, 1)
        print(f"[{page}] Replaced footer-bottom-links")
    else:
        print(f"[{page}] WARNING: Target 2 not found")

    with open(page, "w", encoding="utf-8") as f:
        f.write(content)

print("Footer updates finished!")
