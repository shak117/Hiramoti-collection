/**
 * Hiramoti Collection Satara — Admin Panel & CMS Core Logic
 * Handles Authentication, Real-time Dashboard, Products CRUD,
 * Inline Stock & Price Editing, Image Manager, and Reels Management.
 */

let currentUser = null;
let cachedProducts = [];
let cachedReels = [];
let cachedImages = [];
let cachedEnquiries = [];
let activeSection = "overview";
let pendingConfirmCallback = null;

// ==========================================================================
// 1. INITIALIZATION & AUTHENTICATION
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  checkAuthStatus();
});

async function checkAuthStatus() {
  try {
    const res = await fetch("/api/admin/me");
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated) {
        currentUser = data.user;
        showDashboardUI();
        return;
      }
    }
  } catch (e) {
    console.warn("Auth check error:", e);
  }
  showLoginUI();
}

function showLoginUI() {
  document.getElementById("login-view").style.display = "flex";
  document.getElementById("dashboard-view").style.display = "none";
}

function showDashboardUI() {
  document.getElementById("login-view").style.display = "none";
  document.getElementById("dashboard-view").style.display = "flex";
  
  if (currentUser) {
    const nameEl = document.getElementById("user-display-name");
    if (nameEl) nameEl.textContent = currentUser.username || "Admin";
  }

  // Load all initial data
  loadDashboardData();
  loadProducts();
  loadReels();
  loadImages();
  loadEnquiries();
}

async function handleAdminLogin(e) {
  e.preventDefault();
  const alertEl = document.getElementById("login-alert");
  const btn = document.getElementById("btn-login-submit");
  alertEl.style.display = "none";

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();

  if (!username || !password) {
    alertEl.textContent = "Please enter both username and password.";
    alertEl.style.display = "block";
    return;
  }

  btn.disabled = true;
  btn.innerHTML = "<span>Signing In...</span>";

  try {
    const res = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      currentUser = data.user;
      showToast("Welcome back, " + currentUser.username + "!", "success");
      showDashboardUI();
    } else {
      alertEl.textContent = data.error || "Invalid login credentials.";
      alertEl.style.display = "block";
    }
  } catch (err) {
    alertEl.textContent = "Connection error. Please try again.";
    alertEl.style.display = "block";
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Secure Sign In</span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>`;
  }
}

async function handleAdminLogout() {
  try {
    await fetch("/api/admin/logout", { method: "POST" });
  } catch (e) {}
  currentUser = null;
  showToast("Logged out successfully.", "info");
  showLoginUI();
}

function togglePasswordVisibility(fieldId) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.type = field.type === "password" ? "text" : "password";
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("admin-sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  if (sidebar) sidebar.classList.toggle("open");
  if (overlay) overlay.classList.toggle("open");
}

function closeSidebar() {
  const sidebar = document.getElementById("admin-sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  if (sidebar) sidebar.classList.remove("open");
  if (overlay) overlay.classList.remove("open");
}

function resolveImageUrl(url) {
  if (!url) return "/assets/images/real_reel_DaiL4H0zCqV.jpg";
  const trimmed = String(url).trim();
  if (!trimmed) return "/assets/images/real_reel_DaiL4H0zCqV.jpg";
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://") || trimmed.startsWith("data:") || trimmed.startsWith("blob:")) {
    return trimmed;
  }
  if (trimmed.startsWith("/")) {
    return trimmed;
  }
  if (trimmed.startsWith("../")) {
    return "/" + trimmed.replace(/^\.\.\//, "");
  }
  return "/" + trimmed;
}

// ==========================================================================
// 2. SECTION NAVIGATION
// ==========================================================================
function showSection(sectionId) {
  activeSection = sectionId;
  
  // Close mobile sidebar drawer on navigation
  closeSidebar();

  // Update sidebar active class
  document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
    item.classList.remove("active");
    if (item.dataset.section === sectionId) {
      item.classList.add("active");
    }
  });

  // Update section views
  document.querySelectorAll(".admin-section").forEach(sec => {
    sec.classList.remove("active");
  });
  const activeSec = document.getElementById("section-" + sectionId);
  if (activeSec) activeSec.classList.add("active");

  // Update header title
  const titleEl = document.getElementById("current-section-title");
  const titles = {
    overview: "Dashboard Overview",
    products: "Product Management",
    stock: "Quick Price & Stock Management",
    images: "Image Manager & Media Library",
    reels: "Instagram Reels & Video Feed",
    enquiries: "Showroom Visit Appointments",
    founder: "Founder & Legacy Content Manager",
    settings: "System & Security Settings"
  };
  if (titleEl) titleEl.textContent = titles[sectionId] || "Dashboard";

  // Refresh section data
  if (sectionId === "overview") loadDashboardData();
  if (sectionId === "products") renderProductsTable(cachedProducts);
  if (sectionId === "stock") renderStockTable(cachedProducts);
  if (sectionId === "images") loadImages();
  if (sectionId === "reels") renderReelsCards(cachedReels);
  if (sectionId === "enquiries") loadEnquiries();
  if (sectionId === "founder") loadFounderAdminData();
}

// ==========================================================================
// 3. DASHBOARD OVERVIEW & STATS
// ==========================================================================
async function loadDashboardData() {
  try {
    const res = await fetch("/api/admin/dashboard-stats");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("stat-total-products").textContent = data.total_products || 0;
    document.getElementById("stat-in-stock").textContent = data.in_stock || 0;
    document.getElementById("stat-out-stock").textContent = data.out_of_stock || 0;
    document.getElementById("stat-total-images").textContent = data.total_images || 0;
    document.getElementById("stat-total-reels").textContent = data.total_reels || 0;
    document.getElementById("stat-total-enquiries").textContent = data.total_enquiries || 0;

    // Badges in sidebar
    document.getElementById("badge-products-count").textContent = data.total_products || 0;
    document.getElementById("badge-reels-count").textContent = data.total_reels || 0;
    document.getElementById("badge-enquiries-count").textContent = data.total_enquiries || 0;

    // Render Recent Products in Overview
    const recentProdBody = document.getElementById("overview-recent-products");
    if (data.recent_products && data.recent_products.length > 0) {
      recentProdBody.innerHTML = data.recent_products.map(p => `
        <tr>
          <td>
            <div class="item-cell">
              <img src="../${p.image}" alt="${p.name}" class="item-thumb" onerror="this.src='../assets/images/real_store_shirts.jpg'">
              <div class="item-titles">
                <h4>${p.name}</h4>
                <span>Code: ${p.id}</span>
              </div>
            </div>
          </td>
          <td><strong>₹${p.price}</strong></td>
          <td>${p.stock}</td>
          <td>
            <span class="status-badge ${p.stock > 0 && p.status === 'in_stock' ? 'status-badge-in' : 'status-badge-out'}">
              ${p.stock > 0 && p.status === 'in_stock' ? 'In Stock' : 'Out of Stock'}
            </span>
          </td>
          <td>
            <button class="btn btn-outline-gold btn-sm" onclick="openEditProductModal('${p.id}')">Edit</button>
          </td>
        </tr>
      `).join("");
    } else {
      recentProdBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No products yet.</td></tr>`;
    }

    // Render Recent Enquiries in Overview
    const recentEnqBody = document.getElementById("overview-recent-enquiries");
    if (data.recent_enquiries && data.recent_enquiries.length > 0) {
      recentEnqBody.innerHTML = data.recent_enquiries.map(e => `
        <tr>
          <td><strong>${e.name}</strong></td>
          <td><a href="tel:${e.phone}" style="color: var(--color-gold);">${e.phone}</a></td>
          <td>${e.visit_date || "Open"} ${e.time_slot ? '(' + e.time_slot + ')' : ''}</td>
          <td>
            <a href="https://wa.me/91${e.phone.replace(/[^0-9]/g, '')}?text=Hello%20${encodeURIComponent(e.name)}!%20Regarding%20your%20Hiramoti%20Collection%20visit." target="_blank" class="btn btn-sm btn-gold">
              WhatsApp
            </a>
          </td>
        </tr>
      `).join("");
    } else {
      recentEnqBody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-muted">No appointments booked yet.</td></tr>`;
    }
  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

// ==========================================================================
// 4. PRODUCTS MANAGEMENT (CRUD)
// ==========================================================================
async function loadProducts() {
  try {
    const res = await fetch("/api/admin/products");
    if (res.ok) {
      const data = await res.json();
      cachedProducts = data.products || [];
      renderProductsTable(cachedProducts);
      renderStockTable(cachedProducts);
      populateProductSelectDropdown(cachedProducts);
    }
  } catch (err) {
    console.error("Error loading products:", err);
  }
}

function renderProductsTable(products) {
  const tbody = document.getElementById("products-table-body");
  if (!tbody) return;

  if (products.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-muted">No products found matching filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = products.map(p => `
    <tr>
      <td>
        <div class="item-cell">
          <img src="../${p.image}" alt="${p.name}" class="item-thumb" onerror="this.src='../assets/images/real_store_shirts.jpg'">
          <div class="item-titles">
            <h4>${p.name}</h4>
            <span>${p.marathi_name || ""}</span>
          </div>
        </div>
      </td>
      <td><code>${p.id}</code></td>
      <td>
        <span style="text-transform: capitalize; color: var(--color-gold-light);">${p.category}</span>
        <span style="display: block; font-size: 0.72rem; color: var(--color-white-faint);">${p.subtype.replace('_', ' ')}</span>
      </td>
      <td>
        <span style="font-weight: 700; color: var(--color-white);">₹${p.price}</span>
        ${p.original_price ? `<span style="font-size: 0.75rem; color: var(--color-white-faint); text-decoration: line-through; margin-left: 4px;">₹${p.original_price}</span>` : ""}
      </td>
      <td><strong>${p.stock}</strong></td>
      <td>
        <span class="status-badge ${p.stock > 0 && p.status === 'in_stock' ? 'status-badge-in' : 'status-badge-out'}">
          ${p.stock > 0 && p.status === 'in_stock' ? 'In Stock' : 'Out of Stock'}
        </span>
      </td>
      <td>
        ${p.badge ? `<span class="badge-tag">${p.badge}</span>` : `<span style="color: var(--color-white-faint);">-</span>`}
      </td>
      <td>
        <div class="table-actions">
          <button class="btn-icon" onclick="openEditProductModal('${p.id}')" title="Edit Product">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          </button>
          <button class="btn-icon btn-icon-danger" onclick="confirmDeleteProduct('${p.id}', '${p.name.replace(/'/g, "\\'")}')" title="Delete Product">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
          </button>
        </div>
      </td>
    </tr>
  `).join("");
}

function filterProductsTable() {
  const query = document.getElementById("product-search-input").value.trim().toLowerCase();
  const catFilter = document.getElementById("product-category-filter").value;
  const stockFilter = document.getElementById("product-stock-filter").value;

  const filtered = cachedProducts.filter(p => {
    // Search
    if (query) {
      const name = (p.name || "").toLowerCase();
      const marathi = (p.marathi_name || "").toLowerCase();
      const code = (p.id || "").toLowerCase();
      if (!name.includes(query) && !marathi.includes(query) && !code.includes(query)) {
        return false;
      }
    }
    // Category
    if (catFilter !== "all" && p.category !== catFilter) return false;
    // Stock
    if (stockFilter === "in_stock" && (p.stock <= 0 || p.status !== "in_stock")) return false;
    if (stockFilter === "out_of_stock" && p.stock > 0 && p.status === "in_stock") return false;

    return true;
  });

  renderProductsTable(filtered);
}

function openAddProductModal() {
  document.getElementById("product-modal-title").textContent = "Add New Product";
  document.getElementById("product-id-hidden").value = "";
  document.getElementById("product-form").reset();
  document.getElementById("prod-stock").value = 15;
  document.getElementById("prod-status").value = "in_stock";
  document.getElementById("prod-image").value = "assets/images/real_store_shirts.jpg";
  document.getElementById("product-modal").classList.add("show");
}

function openEditProductModal(productId) {
  const p = cachedProducts.find(item => item.id === productId);
  if (!p) return;

  document.getElementById("product-modal-title").textContent = `Edit Product (${p.id})`;
  document.getElementById("product-id-hidden").value = p.id;
  document.getElementById("prod-name").value = p.name || "";
  document.getElementById("prod-marathi").value = p.marathi_name || "";
  document.getElementById("prod-category").value = p.category || "mens";
  document.getElementById("prod-subtype").value = p.subtype || "jackets";
  document.getElementById("prod-price").value = p.price || "";
  document.getElementById("prod-original-price").value = p.original_price || "";
  document.getElementById("prod-stock").value = p.stock !== undefined ? p.stock : 10;
  document.getElementById("prod-status").value = p.status || "in_stock";
  document.getElementById("prod-badge").value = p.badge || "";
  document.getElementById("prod-sizes").value = p.sizes || "";
  document.getElementById("prod-image").value = p.image || "";
  document.getElementById("prod-reel-url").value = p.reel_url || "";
  document.getElementById("prod-description").value = p.description || "";

  document.getElementById("product-modal").classList.add("show");
}

function closeProductModal() {
  document.getElementById("product-modal").classList.remove("show");
}

async function handleProductFormSubmit(e) {
  e.preventDefault();
  const id = document.getElementById("product-id-hidden").value;
  const isEdit = !!id;

  const payload = {
    name: document.getElementById("prod-name").value.trim(),
    marathi_name: document.getElementById("prod-marathi").value.trim(),
    category: document.getElementById("prod-category").value,
    subtype: document.getElementById("prod-subtype").value,
    price: parseFloat(document.getElementById("prod-price").value),
    original_price: document.getElementById("prod-original-price").value ? parseFloat(document.getElementById("prod-original-price").value) : null,
    stock: parseInt(document.getElementById("prod-stock").value, 10),
    status: document.getElementById("prod-status").value,
    badge: document.getElementById("prod-badge").value.trim(),
    sizes: document.getElementById("prod-sizes").value.trim(),
    image: document.getElementById("prod-image").value.trim(),
    reel_url: document.getElementById("prod-reel-url").value.trim(),
    description: document.getElementById("prod-description").value.trim()
  };

  const btn = document.getElementById("btn-save-product");
  btn.disabled = true;
  btn.textContent = "Saving...";

  try {
    const url = isEdit ? `/api/admin/products/${id}` : "/api/admin/products";
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(isEdit ? "Product updated successfully!" : "New product created!", "success");
      closeProductModal();
      await loadProducts();
      await loadDashboardData();
    } else {
      showToast(data.error || "Failed to save product", "danger");
    }
  } catch (err) {
    showToast("Network error while saving product", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Product";
  }
}

function confirmDeleteProduct(productId, productName) {
  openConfirmModal(
    "Delete Product",
    `Are you sure you want to delete this product? This action cannot be undone.<br><br><strong>${productName}</strong> (<code>${productId}</code>)`,
    async () => {
      try {
        const res = await fetch(`/api/admin/products/${productId}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(`Product '${productName}' deleted.`, "success");
          await loadProducts();
          await loadDashboardData();
        } else {
          showToast(data.error || "Failed to delete product", "danger");
        }
      } catch (err) {
        showToast("Error deleting product", "danger");
      }
    }
  );
}

// ==========================================================================
// 5. QUICK PRICE & STOCK MANAGEMENT
// ==========================================================================
function renderStockTable(products) {
  const tbody = document.getElementById("stock-table-body");
  if (!tbody) return;

  if (products.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-muted">No products in catalog.</td></tr>`;
    return;
  }

  tbody.innerHTML = products.map(p => `
    <tr id="stock-row-${p.id}">
      <td>
        <div class="item-cell">
          <img src="../${p.image}" alt="${p.name}" class="item-thumb" onerror="this.src='../assets/images/real_store_shirts.jpg'">
          <div class="item-titles">
            <h4>${p.name}</h4>
            <span>${p.id}</span>
          </div>
        </div>
      </td>
      <td>
        <span style="text-transform: capitalize; color: var(--color-gold-light);">${p.category}</span>
      </td>
      <td>
        <input type="number" id="quick-price-${p.id}" class="quick-edit-input" value="${p.price}" min="1" step="1">
      </td>
      <td>
        <input type="number" id="quick-stock-${p.id}" class="quick-edit-input" value="${p.stock}" min="0" step="1" oninput="handleStockInputLive('${p.id}', this.value)">
      </td>
      <td>
        <span id="quick-badge-${p.id}" class="status-badge ${p.stock > 0 && p.status === 'in_stock' ? 'status-badge-in' : 'status-badge-out'}">
          ${p.stock > 0 && p.status === 'in_stock' ? 'In Stock' : 'Out of Stock'}
        </span>
      </td>
      <td>
        <button class="btn btn-gold btn-sm" onclick="saveQuickPriceStock('${p.id}')">
          Save
        </button>
      </td>
    </tr>
  `).join("");
}

function handleStockInputLive(productId, newQty) {
  const badge = document.getElementById(`quick-badge-${productId}`);
  if (!badge) return;
  const qty = parseInt(newQty, 10);
  if (isNaN(qty) || qty <= 0) {
    badge.className = "status-badge status-badge-out";
    badge.textContent = "Out of Stock";
  } else {
    badge.className = "status-badge status-badge-in";
    badge.textContent = "In Stock";
  }
}

async function saveQuickPriceStock(productId) {
  const priceInput = document.getElementById(`quick-price-${productId}`);
  const stockInput = document.getElementById(`quick-stock-${productId}`);
  if (!priceInput || !stockInput) return;

  const price = parseFloat(priceInput.value);
  const stock = parseInt(stockInput.value, 10);

  if (isNaN(price) || price <= 0) {
    showToast("Please enter a valid price.", "danger");
    return;
  }
  if (isNaN(stock) || stock < 0) {
    showToast("Please enter a valid stock quantity (0 or more).", "danger");
    return;
  }

  const payload = {
    price: price,
    stock: stock,
    status: stock === 0 ? "out_of_stock" : "in_stock"
  };

  try {
    const res = await fetch(`/api/admin/products/${productId}/quick-update`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`Updated '${data.product.name}': ₹${price}, Stock: ${stock}`, "success");
      // Update local cache
      const idx = cachedProducts.findIndex(p => p.id === productId);
      if (idx !== -1) {
        cachedProducts[idx] = data.product;
      }
      await loadDashboardData();
    } else {
      showToast(data.error || "Failed to update", "danger");
    }
  } catch (err) {
    showToast("Network error saving price & stock", "danger");
  }
}

// ==========================================================================
// 6. IMAGE MANAGER
// ==========================================================================
let selectedImageFile = null;

function handleImageFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  // Validate size (max 10MB)
  if (file.size > 10 * 1024 * 1024) {
    showToast("File is too large. Max size is 10 MB.", "danger");
    e.target.value = "";
    return;
  }

  selectedImageFile = file;
  const reader = new FileReader();
  reader.onload = (event) => {
    document.getElementById("preview-img").src = event.target.result;
    document.getElementById("preview-filename").textContent = file.name;
    document.getElementById("preview-filesize").textContent = (file.size / 1024).toFixed(1) + " KB";
    document.getElementById("dropzone-prompt").style.display = "none";
    document.getElementById("dropzone-preview").style.display = "flex";
  };
  reader.readAsDataURL(file);
}

function clearImagePreview() {
  selectedImageFile = null;
  document.getElementById("image-file-input").value = "";
  document.getElementById("dropzone-prompt").style.display = "block";
  document.getElementById("dropzone-preview").style.display = "none";
}

async function handleImageUpload(e) {
  e.preventDefault();
  if (!selectedImageFile) {
    showToast("Please choose an image to upload.", "danger");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedImageFile);

  const prodSelect = document.getElementById("image-product-association");
  if (prodSelect && prodSelect.value) {
    formData.append("product_id", prodSelect.value);
  }

  const isPrimary = document.getElementById("image-is-primary").checked;
  formData.append("is_primary", isPrimary ? "true" : "false");

  const btn = document.getElementById("btn-upload-submit");
  btn.disabled = true;
  btn.textContent = "Uploading...";

  try {
    const res = await fetch("/api/admin/upload-image", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast("Image uploaded successfully!", "success");
      clearImagePreview();
      await loadImages();
      await loadProducts();
      await loadDashboardData();
    } else {
      showToast(data.error || "Upload failed", "danger");
    }
  } catch (err) {
    showToast("Error uploading image", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Upload & Save Image";
  }
}

async function loadImages() {
  try {
    const res = await fetch("/api/admin/images");
    if (res.ok) {
      const data = await res.json();
      cachedImages = data.images || [];
      renderImagesGallery(cachedImages);
    }
  } catch (err) {
    console.error("Error loading images:", err);
  }
}

function renderImagesGallery(images) {
  const grid = document.getElementById("images-grid");
  const countEl = document.getElementById("images-count-label");
  if (!grid) return;

  if (countEl) countEl.textContent = `${images.length} available images`;

  if (images.length === 0) {
    grid.innerHTML = `<div class="text-center col-span-full py-8 text-muted">No images found.</div>`;
    return;
  }

  grid.innerHTML = images.map(img => `
    <div class="image-card">
      <div class="image-card-thumb">
        <img src="../${img.url}" alt="${img.filename}" loading="lazy" onerror="this.src='../assets/images/real_store_shirts.jpg'">
      </div>
      <div class="image-card-info">
        <div class="image-card-name" title="${img.filename}">${img.filename}</div>
        <div class="image-card-meta">
          <span>${img.size_kb} KB</span>
          <span style="text-transform: capitalize;">${img.source.replace('_', ' ')}</span>
        </div>
        <div class="image-card-actions">
          <button class="btn btn-outline btn-sm" style="flex: 1; padding: 4px;" onclick="copyImageUrl('${img.url}')">Copy URL</button>
          ${img.source === 'uploads' ? `
            <button class="btn btn-icon btn-icon-danger" onclick="confirmDeleteImage('${img.filename}')" title="Delete Image">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          ` : ""}
        </div>
      </div>
    </div>
  `).join("");
}

function copyImageUrl(url) {
  navigator.clipboard.writeText(url).then(() => {
    showToast("Image path copied to clipboard: " + url, "info");
  }).catch(() => {
    showToast("Path: " + url, "info");
  });
}

function confirmDeleteImage(filename) {
  openConfirmModal(
    "Delete Image",
    `Are you sure you want to delete this uploaded image? This action cannot be undone.<br><br><code>${filename}</code>`,
    async () => {
      try {
        const res = await fetch(`/api/admin/images/${filename}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast("Image deleted successfully.", "success");
          await loadImages();
          await loadDashboardData();
        } else {
          showToast(data.error || "Failed to delete image", "danger");
        }
      } catch (err) {
        showToast("Error deleting image", "danger");
      }
    }
  );
}

function populateProductSelectDropdown(products) {
  const select = document.getElementById("image-product-association");
  if (!select) return;
  select.innerHTML = `<option value="">-- Standalone Gallery / Showroom Asset --</option>` +
    products.map(p => `<option value="${p.id}">${p.name} (${p.id})</option>`).join("");
}

function chooseImageForProduct() {
  if (cachedImages.length > 0) {
    const choice = prompt("Enter an image path or pick from available:\n\n" + cachedImages.slice(0, 10).map(i => i.url).join("\n"), cachedImages[0].url);
    if (choice) {
      document.getElementById("prod-image").value = choice.trim();
    }
  } else {
    showToast("No images available. Please upload one in Image Manager.", "info");
  }
}

// ==========================================================================
// 7. REELS & VIDEOS MANAGEMENT
// ==========================================================================
async function loadReels() {
  try {
    const res = await fetch("/api/admin/reels");
    if (res.ok) {
      const data = await res.json();
      cachedReels = data.reels || [];
      renderReelsCards(cachedReels);
    }
  } catch (err) {
    console.error("Error loading reels:", err);
  }
}

function renderReelsCards(reels) {
  const grid = document.getElementById("admin-reels-grid");
  if (!grid) return;

  if (reels.length === 0) {
    grid.innerHTML = `<div class="text-center col-span-full py-8 text-muted">No Instagram reels registered.</div>`;
    return;
  }

  grid.innerHTML = reels.map(r => `
    <div class="admin-reel-card">
      <div class="admin-reel-thumb-wrapper">
        <img src="${resolveImageUrl(r.image)}" alt="${r.title}" onerror="this.onerror=null; this.src='/assets/images/real_reel_DaiL4H0zCqV.jpg';">
        <button class="reel-play-overlay-btn" onclick="previewReel('${r.embed_url}', '${r.title.replace(/'/g, "\\'")}')" title="Watch Reel">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <span class="badge-tag" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7);">
          Order #${r.display_order}
        </span>
        <span class="badge-tag" style="position: absolute; top: 10px; right: 10px; background: var(--color-burgundy); color: #fff;">
          ${r.price || "OFFER"}
        </span>
      </div>
      <div class="admin-reel-content">
        <div class="admin-reel-header">
          <div>
            <h4>${r.title}</h4>
            <span style="font-size: 0.75rem; color: var(--color-gold-light); font-family: var(--font-marathi);">${r.marathi_title || ""}</span>
          </div>
          <span class="status-badge ${r.is_active ? 'status-badge-in' : 'status-badge-out'}">
            ${r.is_active ? 'Active' : 'Disabled'}
          </span>
        </div>
        <p class="admin-reel-caption">${r.caption || "No caption provided."}</p>
        <div class="admin-reel-footer">
          <a href="${r.url}" target="_blank" rel="noopener" class="btn-link" style="font-size: 0.75rem;">
            View on Instagram &nearr;
          </a>
          <div class="table-actions">
            <button class="btn-icon" onclick="openEditReelModal('${r.id}')" title="Edit Reel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
            <button class="btn-icon btn-icon-danger" onclick="confirmDeleteReel('${r.id}', '${r.title.replace(/'/g, "\\'")}')" title="Delete Reel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join("");
}

// --- Reel Media Uploader Logic ---
let isUploadingReelCover = false;
let isUploadingReelVideo = false;

function handleReelCoverFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  const validExts = ["jpg", "jpeg", "png", "webp"];
  const ext = file.name.split(".").pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToast(`Invalid image format (.${ext}). Allowed: .jpg, .jpeg, .png, .webp`, "danger");
    e.target.value = "";
    return;
  }

  // Max 15 MB
  if (file.size > 15 * 1024 * 1024) {
    showToast(`Cover image is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Max limit is 15 MB.`, "danger");
    e.target.value = "";
    return;
  }

  // Instant local preview
  const localUrl = URL.createObjectURL(file);
  const thumb = document.getElementById("reel-preview-thumb");
  if (thumb) thumb.src = localUrl;

  const filenameLabel = document.getElementById("reel-cover-filename-label");
  if (filenameLabel) filenameLabel.textContent = `Selected: ${file.name} (Uploading...)`;

  const pathDisplay = document.getElementById("reel-cover-path-display");
  if (pathDisplay) pathDisplay.textContent = `Uploading from device: ${file.name}`;

  const badge = document.getElementById("reel-cover-badge");
  if (badge) {
    badge.textContent = "Uploading...";
    badge.className = "badge-cover-source";
  }

  // Upload immediately to backend storage
  isUploadingReelCover = true;
  const formData = new FormData();
  formData.append("file", file);
  formData.append("media_type", "image");

  fetch("/api/admin/upload-media", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      isUploadingReelCover = false;
      if (data.success && data.url) {
        document.getElementById("reel-image-hidden").value = data.url;
        if (filenameLabel) filenameLabel.textContent = `Selected: ${file.name}`;
        if (pathDisplay) pathDisplay.textContent = data.url;
        if (badge) {
          badge.textContent = "Uploaded Device Cover";
          badge.className = "badge-cover-source badge-uploaded";
        }
        if (thumb) thumb.src = resolveImageUrl(data.url);
        showToast("Reel cover image uploaded successfully!", "success");
      } else {
        showToast(data.error || "Image upload failed", "danger");
        if (filenameLabel) filenameLabel.textContent = "Upload failed — try again";
      }
    })
    .catch(err => {
      isUploadingReelCover = false;
      showToast("Network error uploading cover image", "danger");
      if (filenameLabel) filenameLabel.textContent = "Upload failed";
    });
}

function clearReelCoverImage() {
  const fileInput = document.getElementById("reel-cover-file");
  if (fileInput) fileInput.value = "";

  const defaultImg = "assets/images/real_reel_DaiL4H0zCqV.jpg";
  document.getElementById("reel-image-hidden").value = defaultImg;

  const filenameLabel = document.getElementById("reel-cover-filename-label");
  if (filenameLabel) filenameLabel.textContent = "Default Store Cover";

  const pathDisplay = document.getElementById("reel-cover-path-display");
  if (pathDisplay) pathDisplay.textContent = defaultImg;

  const badge = document.getElementById("reel-cover-badge");
  if (badge) {
    badge.textContent = "Default Cover";
    badge.className = "badge-cover-source";
  }

  const thumb = document.getElementById("reel-preview-thumb");
  if (thumb) thumb.src = resolveImageUrl(defaultImg);

  showToast("Reel cover reset to default store artwork", "info");
}

function handleReelVideoFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  const validExts = ["mp4", "webm", "mov"];
  const ext = file.name.split(".").pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToast(`Invalid video format (.${ext}). Allowed: .mp4, .webm, .mov`, "danger");
    e.target.value = "";
    return;
  }

  // Max 50 MB
  if (file.size > 50 * 1024 * 1024) {
    showToast(`Video is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Max limit is 50 MB.`, "danger");
    e.target.value = "";
    return;
  }

  const progressWrap = document.getElementById("reel-video-progress-wrap");
  const progressBar = document.getElementById("reel-video-progress-bar");
  const progressLabel = document.getElementById("reel-video-progress-label");
  const statusText = document.getElementById("reel-video-status-text");

  if (progressWrap) progressWrap.style.display = "flex";
  if (progressBar) progressBar.style.width = "0%";
  if (progressLabel) progressLabel.textContent = "0%";
  if (statusText) statusText.textContent = `Uploading ${file.name}...`;

  isUploadingReelVideo = true;
  const formData = new FormData();
  formData.append("file", file);
  formData.append("media_type", "video");

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/admin/upload-media", true);

  xhr.upload.onprogress = (evt) => {
    if (evt.lengthComputable && progressBar && progressLabel) {
      const pct = Math.round((evt.loaded / evt.total) * 100);
      progressBar.style.width = pct + "%";
      progressLabel.textContent = pct + "%";
    }
  };

  xhr.onload = () => {
    isUploadingReelVideo = false;
    if (progressWrap) progressWrap.style.display = "none";

    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const data = JSON.parse(xhr.responseText);
        if (data.success && data.url) {
          document.getElementById("reel-video-url-hidden").value = data.url;
          if (statusText) statusText.textContent = `Selected: ${file.name}`;

          const previewCard = document.getElementById("reel-video-preview-card");
          const videoElement = document.getElementById("reel-video-element");
          const nameDisplay = document.getElementById("reel-video-name-display");

          if (videoElement) {
            videoElement.src = resolveImageUrl(data.url);
          }
          if (nameDisplay) {
            nameDisplay.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
          }
          if (previewCard) {
            previewCard.style.display = "block";
          }

          // Auto-fill title if empty
          const titleInput = document.getElementById("reel-title");
          if (!titleInput.value.trim()) {
            titleInput.value = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
          }

          showToast("Reel video uploaded successfully!", "success");
        } else {
          showToast(data.error || "Video upload failed", "danger");
          if (statusText) statusText.textContent = "Upload failed";
        }
      } catch (err) {
        showToast("Invalid response parsing upload result", "danger");
      }
    } else {
      showToast("Server rejected video upload. Status: " + xhr.status, "danger");
      if (statusText) statusText.textContent = "Upload failed";
    }
  };

  xhr.onerror = () => {
    isUploadingReelVideo = false;
    if (progressWrap) progressWrap.style.display = "none";
    showToast("Network error during video upload", "danger");
    if (statusText) statusText.textContent = "Upload failed";
  };

  xhr.send(formData);
}

function clearReelVideo() {
  const fileInput = document.getElementById("reel-video-file");
  if (fileInput) fileInput.value = "";

  document.getElementById("reel-video-url-hidden").value = "";

  const statusText = document.getElementById("reel-video-status-text");
  if (statusText) statusText.textContent = "No video selected";

  const videoElement = document.getElementById("reel-video-element");
  if (videoElement) {
    videoElement.pause();
    videoElement.src = "";
  }

  const previewCard = document.getElementById("reel-video-preview-card");
  if (previewCard) previewCard.style.display = "none";

  const progressWrap = document.getElementById("reel-video-progress-wrap");
  if (progressWrap) progressWrap.style.display = "none";
}

function openAddReelModal() {
  document.getElementById("reel-modal-title").textContent = "Add New Reel";
  document.getElementById("reel-id-hidden").value = "";
  document.getElementById("reel-form").reset();
  document.getElementById("reel-is-active").checked = true;
  document.getElementById("reel-order").value = (cachedReels.length + 1);

  clearReelCoverImage();
  clearReelVideo();

  document.getElementById("reel-modal").classList.add("show");
}

function openEditReelModal(reelId) {
  const r = cachedReels.find(item => item.id === reelId);
  if (!r) return;

  document.getElementById("reel-modal-title").textContent = `Edit Reel (${r.id})`;
  document.getElementById("reel-id-hidden").value = r.id;
  document.getElementById("reel-url").value = r.url || "";
  document.getElementById("reel-title").value = r.title || "";
  document.getElementById("reel-marathi").value = r.marathi_title || "";
  document.getElementById("reel-price").value = r.price || "";
  document.getElementById("reel-offer").value = r.offer || "";
  document.getElementById("reel-order").value = r.display_order || 1;
  document.getElementById("reel-caption").value = r.caption || "";
  document.getElementById("reel-is-active").checked = !!r.is_active;

  // Set Cover Image state
  const currentImg = r.image || "assets/images/real_reel_DaiL4H0zCqV.jpg";
  document.getElementById("reel-image-hidden").value = currentImg;
  const filename = currentImg.split("/").pop();
  const isUploaded = currentImg.includes("uploads/");

  const filenameLabel = document.getElementById("reel-cover-filename-label");
  if (filenameLabel) filenameLabel.textContent = `Selected: ${filename}`;

  const pathDisplay = document.getElementById("reel-cover-path-display");
  if (pathDisplay) pathDisplay.textContent = currentImg;

  const badge = document.getElementById("reel-cover-badge");
  if (badge) {
    badge.textContent = isUploaded ? "Uploaded Custom Cover" : "Current Cover";
    badge.className = isUploaded ? "badge-cover-source badge-uploaded" : "badge-cover-source";
  }

  const thumb = document.getElementById("reel-preview-thumb");
  if (thumb) thumb.src = resolveImageUrl(currentImg);

  // Set Video state
  const vidUrl = r.video_url || (r.embed_url && (r.embed_url.endsWith(".mp4") || r.embed_url.endsWith(".webm") || r.embed_url.endsWith(".mov")) ? r.embed_url : "");
  if (vidUrl) {
    document.getElementById("reel-video-url-hidden").value = vidUrl;
    const vName = vidUrl.split("/").pop();
    const statusText = document.getElementById("reel-video-status-text");
    if (statusText) statusText.textContent = `Attached: ${vName}`;

    const nameDisplay = document.getElementById("reel-video-name-display");
    if (nameDisplay) nameDisplay.textContent = vName;

    const vidEl = document.getElementById("reel-video-element");
    if (vidEl) vidEl.src = resolveImageUrl(vidUrl);

    const previewCard = document.getElementById("reel-video-preview-card");
    if (previewCard) previewCard.style.display = "block";
  } else {
    clearReelVideo();
  }

  document.getElementById("reel-modal").classList.add("show");
}

function closeReelModal() {
  document.getElementById("reel-modal").classList.remove("show");
}

function handleReelUrlInput(url) {
  // If user pasted Instagram URL, auto-set default title/badge if empty
  if (url.includes("instagram.com/reel/")) {
    const match = url.match(/reel\/([A-Za-z0-9_-]+)/);
    if (match && !document.getElementById("reel-title").value) {
      document.getElementById("reel-title").value = "Trending Instagram Reel (" + match[1] + ")";
    }
  }
}

async function handleReelFormSubmit(e) {
  e.preventDefault();

  if (isUploadingReelCover) {
    showToast("Please wait until the cover image finishes uploading.", "warning");
    return;
  }
  if (isUploadingReelVideo) {
    showToast("Please wait until the reel video finishes uploading.", "warning");
    return;
  }

  const id = document.getElementById("reel-id-hidden").value;
  const isEdit = !!id;

  const rawImage = document.getElementById("reel-image-hidden").value.trim();
  const imageVal = rawImage || "assets/images/real_reel_DaiL4H0zCqV.jpg";

  const reelUrl = document.getElementById("reel-url").value.trim();
  const videoUrl = document.getElementById("reel-video-url-hidden").value.trim();

  if (!reelUrl && !videoUrl) {
    showToast("Please provide either an Instagram Reel URL or upload a Reel Video.", "danger");
    return;
  }

  const payload = {
    url: reelUrl,
    video_url: videoUrl,
    title: document.getElementById("reel-title").value.trim(),
    marathi_title: document.getElementById("reel-marathi").value.trim(),
    price: document.getElementById("reel-price").value.trim(),
    offer: document.getElementById("reel-offer").value.trim(),
    display_order: parseInt(document.getElementById("reel-order").value, 10) || 1,
    image: imageVal,
    caption: document.getElementById("reel-caption").value.trim(),
    is_active: document.getElementById("reel-is-active").checked
  };

  const btn = document.getElementById("btn-save-reel");
  btn.disabled = true;
  btn.textContent = "Saving...";

  try {
    const url = isEdit ? `/api/admin/reels/${id}` : "/api/admin/reels";
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(isEdit ? "Reel updated successfully!" : "Reel added to showcase!", "success");
      closeReelModal();
      
      // Update local cache immediately
      if (data.reel) {
        const idx = cachedReels.findIndex(item => item.id === data.reel.id);
        if (idx !== -1) {
          cachedReels[idx] = data.reel;
        } else {
          cachedReels.push(data.reel);
        }
        renderReelsCards(cachedReels);
      }
      
      await loadReels();
      await loadDashboardData();
    } else {
      showToast(data.error || "Failed to save reel", "danger");
    }
  } catch (err) {
    showToast("Network error saving reel", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Reel";
  }
}

function previewReel(embedUrl, title) {
  const iframe = document.getElementById("admin-reel-iframe");
  const video = document.getElementById("admin-reel-video");
  const titleEl = document.getElementById("preview-reel-title");
  if (titleEl) titleEl.textContent = title;

  const isVideo = embedUrl && (embedUrl.endsWith(".mp4") || embedUrl.endsWith(".webm") || embedUrl.endsWith(".mov") || embedUrl.includes("uploads/hm_vid"));

  if (isVideo) {
    if (iframe) {
      iframe.src = "";
      iframe.style.display = "none";
    }
    if (video) {
      video.src = resolveImageUrl(embedUrl);
      video.style.display = "block";
      video.play().catch(() => {});
    }
  } else {
    if (video) {
      video.pause();
      video.src = "";
      video.style.display = "none";
    }
    if (iframe && embedUrl) {
      iframe.src = embedUrl;
      iframe.style.display = "block";
    }
  }

  document.getElementById("reel-preview-modal").classList.add("show");
}

function closeReelPreviewModal() {
  const iframe = document.getElementById("admin-reel-iframe");
  const video = document.getElementById("admin-reel-video");
  if (iframe) iframe.src = "";
  if (video) {
    video.pause();
    video.src = "";
  }
  document.getElementById("reel-preview-modal").classList.remove("show");
}

function confirmDeleteReel(reelId, reelTitle) {
  openConfirmModal(
    "Delete Reel",
    `Are you sure you want to delete this reel? It will be removed from the public website feed.<br><br><strong>${reelTitle}</strong>`,
    async () => {
      try {
        const res = await fetch(`/api/admin/reels/${reelId}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(`Reel '${reelTitle}' deleted.`, "success");
          await loadReels();
          await loadDashboardData();
        } else {
          showToast(data.error || "Failed to delete reel", "danger");
        }
      } catch (err) {
        showToast("Error deleting reel", "danger");
      }
    }
  );
}

// ==========================================================================
// 8. SHOWROOM ENQUIRIES / APPOINTMENTS
// ==========================================================================
async function loadEnquiries() {
  try {
    const res = await fetch("/api/admin/enquiries");
    if (res.ok) {
      const data = await res.json();
      cachedEnquiries = data.enquiries || [];
      renderEnquiriesTable(cachedEnquiries);
    }
  } catch (err) {
    console.error("Error loading enquiries:", err);
  }
}

function renderEnquiriesTable(enquiries) {
  const tbody = document.getElementById("enquiries-table-body");
  const countEl = document.getElementById("enquiries-count-label");
  if (!tbody) return;

  if (countEl) countEl.textContent = `${enquiries.length} appointments booked`;

  if (enquiries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-muted">No appointments booked yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = enquiries.map(e => `
    <tr>
      <td><strong>${e.name}</strong></td>
      <td>
        <a href="tel:${e.phone}" style="color: var(--color-gold); font-weight: 600;">${e.phone}</a>
      </td>
      <td>${e.area || "Satara"}</td>
      <td>
        <strong>${e.visit_date || "Open Visit"}</strong>
        ${e.time_slot ? `<span style="display: block; font-size: 0.75rem; color: var(--color-white-faint);">${e.time_slot}</span>` : ""}
      </td>
      <td>
        <span class="badge-tag">${e.style_interest || "All Collections"}</span>
      </td>
      <td style="font-size: 0.75rem; color: var(--color-white-faint);">${e.created_at || "Recent"}</td>
      <td>
        <a href="https://wa.me/91${e.phone.replace(/[^0-9]/g, '')}?text=Hello%20${encodeURIComponent(e.name)}!%20Thank%20you%20for%20booking%20a%20visit%20at%20Hiramoti%20Collection%20Satara." target="_blank" rel="noopener" class="btn btn-gold btn-sm">
          WhatsApp
        </a>
      </td>
      <td>
        <button class="btn-icon btn-icon-danger" onclick="confirmDeleteEnquiry(${e.id}, '${e.name.replace(/'/g, "\\'")}')" title="Delete Appointment">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </td>
    </tr>
  `).join("");
}

function confirmDeleteEnquiry(id, customerName) {
  openConfirmModal(
    "Delete Showroom Appointment",
    "Are you sure you want to delete this showroom appointment?",
    async () => {
      try {
        const res = await fetch(`/api/admin/enquiries/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast("Showroom appointment deleted successfully.", "success");
          await loadEnquiries();
          await loadDashboardData();
        } else {
          showToast(data.error || "Failed to delete appointment", "danger");
        }
      } catch (err) {
        showToast("Error deleting appointment", "danger");
      }
    },
    "Delete"
  );
}

// ==========================================================================
// 9. SETTINGS & SECURE MOBILE OTP PASSWORD CHANGE
// ==========================================================================
let otpCountdownInterval = null;
let otpCooldownInterval = null;
let currentOtpResetToken = null;

async function handleRequestOtp() {
  const alertEl = document.getElementById("pwd-alert");
  if (alertEl) alertEl.style.display = "none";

  const btnRequest = document.getElementById("btn-request-otp");
  const btnResend = document.getElementById("btn-resend-otp");
  if (btnRequest) {
    btnRequest.disabled = true;
    btnRequest.innerHTML = "<span>Sending OTP...</span>";
  }
  if (btnResend) btnResend.disabled = true;

  try {
    const res = await fetch("/api/admin/otp/request", { method: "POST" });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast(data.message || "Verification code sent to registered mobile!", "success");
      
      // Transition to Step 2
      const step1 = document.getElementById("otp-step-1");
      const step2 = document.getElementById("otp-step-2");
      const step3 = document.getElementById("otp-step-3");
      if (step1) step1.classList.remove("active");
      if (step2) step2.classList.add("active");
      if (step3) step3.classList.remove("active");

      // Focus OTP input
      const codeInput = document.getElementById("otp-code-input");
      if (codeInput) {
        codeInput.value = "";
        setTimeout(() => codeInput.focus(), 150);
      }

      // Start 5-minute countdown
      startOtpTimer(data.expires_in || 300);

      // Start 30-second resend cooldown
      startResendCooldown(data.cooldown || 30);
    } else {
      showToast(data.error || "Failed to send OTP", "danger");
    }
  } catch (err) {
    showToast("Network error requesting verification code.", "danger");
  } finally {
    if (btnRequest) {
      btnRequest.disabled = false;
      btnRequest.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg><span>Send Verification OTP</span>`;
    }
  }
}

function startOtpTimer(durationSeconds) {
  if (otpCountdownInterval) clearInterval(otpCountdownInterval);
  let remaining = durationSeconds;
  const timerEl = document.getElementById("otp-timer");

  function update() {
    const mins = Math.floor(remaining / 60);
    const secs = remaining % 60;
    if (timerEl) {
      timerEl.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }
    if (remaining <= 0) {
      clearInterval(otpCountdownInterval);
      if (timerEl) timerEl.textContent = "Expired";
      showToast("OTP has expired. Please click Resend OTP.", "danger");
    }
    remaining--;
  }

  update();
  otpCountdownInterval = setInterval(update, 1000);
}

function startResendCooldown(seconds) {
  if (otpCooldownInterval) clearInterval(otpCooldownInterval);
  let remaining = seconds;
  const btnResend = document.getElementById("btn-resend-otp");
  if (!btnResend) return;
  btnResend.disabled = true;

  function update() {
    if (remaining <= 0) {
      clearInterval(otpCooldownInterval);
      btnResend.disabled = false;
      btnResend.textContent = "Resend OTP";
    } else {
      btnResend.textContent = `Resend in ${remaining}s`;
      remaining--;
    }
  }

  update();
  otpCooldownInterval = setInterval(update, 1000);
}

async function handleVerifyOtp() {
  const codeInput = document.getElementById("otp-code-input");
  const code = codeInput ? codeInput.value.trim() : "";
  const btn = document.getElementById("btn-verify-otp");

  if (!code || code.length !== 6 || !/^\d{6}$/.test(code)) {
    showToast("Please enter a valid 6-digit numeric OTP.", "danger");
    if (codeInput) codeInput.focus();
    return;
  }

  btn.disabled = true;
  btn.textContent = "Verifying...";

  try {
    const res = await fetch("/api/admin/otp/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp: code })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      currentOtpResetToken = data.reset_token;
      if (otpCountdownInterval) clearInterval(otpCountdownInterval);
      if (otpCooldownInterval) clearInterval(otpCooldownInterval);

      showToast("Mobile verified successfully! Set your new password.", "success");

      // Switch to Step 3
      const step1 = document.getElementById("otp-step-1");
      const step2 = document.getElementById("otp-step-2");
      const step3 = document.getElementById("otp-step-3");
      if (step1) step1.classList.remove("active");
      if (step2) step2.classList.remove("active");
      if (step3) step3.classList.add("active");

      const newPwd = document.getElementById("pwd-new");
      if (newPwd) setTimeout(() => newPwd.focus(), 150);
    } else {
      showToast(data.error || "Invalid OTP code", "danger");
    }
  } catch (err) {
    showToast("Error verifying OTP code", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Verify Code & Continue";
  }
}

async function handleFinalPasswordChange(e) {
  e.preventDefault();
  const alertEl = document.getElementById("pwd-alert");
  if (alertEl) alertEl.style.display = "none";

  const new_password = document.getElementById("pwd-new").value;
  const confirm_password = document.getElementById("pwd-confirm").value;

  if (!currentOtpResetToken) {
    showToast("Please complete mobile OTP verification first.", "danger");
    resetOtpWizard();
    return;
  }

  if (new_password.length < 8) {
    showToast("New password must be at least 8 characters long.", "danger");
    return;
  }

  if (new_password !== confirm_password) {
    showToast("New password and confirmation do not match.", "danger");
    return;
  }

  const btn = document.getElementById("btn-submit-new-pwd");
  btn.disabled = true;
  btn.textContent = "Updating Password...";

  try {
    const res = await fetch("/api/admin/change-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reset_token: currentOtpResetToken,
        new_password: new_password,
        confirm_password: confirm_password
      })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast("Password updated successfully! Please log in with your new credentials.", "success");
      resetOtpWizard();
      setTimeout(() => {
        currentUser = null;
        showLoginUI();
        const loginAlert = document.getElementById("login-alert");
        if (loginAlert) {
          loginAlert.className = "admin-alert admin-alert-success";
          loginAlert.textContent = "Password updated! Please sign in with your new credentials.";
          loginAlert.style.display = "block";
        }
      }, 1500);
    } else {
      showToast(data.error || "Failed to update password", "danger");
    }
  } catch (err) {
    showToast("Error updating password", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Update Password & Re-authenticate";
  }
}

function resetOtpWizard() {
  if (otpCountdownInterval) clearInterval(otpCountdownInterval);
  if (otpCooldownInterval) clearInterval(otpCooldownInterval);
  currentOtpResetToken = null;

  const step1 = document.getElementById("otp-step-1");
  const step2 = document.getElementById("otp-step-2");
  const step3 = document.getElementById("otp-step-3");
  if (step1) step1.classList.add("active");
  if (step2) step2.classList.remove("active");
  if (step3) step3.classList.remove("active");

  const codeInput = document.getElementById("otp-code-input");
  if (codeInput) codeInput.value = "";
  const pwdNew = document.getElementById("pwd-new");
  if (pwdNew) pwdNew.value = "";
  const pwdConfirm = document.getElementById("pwd-confirm");
  if (pwdConfirm) pwdConfirm.value = "";
}

// ==========================================================================
// 10. CONFIRMATION MODAL & TOASTS
// ==========================================================================
function openConfirmModal(title, message, onConfirm, confirmBtnText = "Confirm Delete") {
  document.getElementById("confirm-title").textContent = title;
  document.getElementById("confirm-message").innerHTML = message;
  pendingConfirmCallback = onConfirm;

  const proceedBtn = document.getElementById("btn-confirm-proceed");
  proceedBtn.textContent = confirmBtnText;
  proceedBtn.onclick = () => {
    if (pendingConfirmCallback) pendingConfirmCallback();
    closeConfirmModal();
  };

  document.getElementById("confirm-modal").classList.add("show");
}

function closeConfirmModal() {
  pendingConfirmCallback = null;
  document.getElementById("confirm-modal").classList.remove("show");
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// ==========================================================================
// 11. FOUNDER & LEGACY CMS MANAGEMENT
// ==========================================================================
let cachedFounderData = {
  founder: {
    name: "Late Shri Ujwal Rathi",
    designation: "Founder, Hiramoti Collection",
    photo: "assets/images/hiramoti_founder_home.jpg",
    quote: "Trust is not given — it is earned, stitch by stitch, customer by customer.",
    quote_author: "Late Shri Ujwal Rathi",
    biography: "Late Shri Ujwal Rathi laid the cornerstone of Hiramoti Collection in 1987 with a heartfelt vision: to provide the people of Satara with exquisite garments, genuine hospitality, and unquestionable trust. Under his dedicated leadership, Hiramoti Collection became far more than a clothing store — it became an enduring institution in the historic heart of Satara.\n\nHis commitment to welcoming every customer as family and ensuring fair pricing without compromising on fabric quality established standards that guide the showroom to this very day."
  },
  milestones: [
    {
      year: "1987",
      badge_sub: "Origin",
      tag: "The Beginning • Vision • Trust",
      title: "The Beginning",
      description: "Hiramoti Collection was founded in 1987 with a singular vision — to bring premium-quality clothing, honest pricing, and genuine trust to the people of Satara. From humble beginnings, it was built on deep relationships with every customer who walked through the doors.",
      quote: "Where trust and honest craftsmanship were first woven into our story.",
      image: "assets/images/hiramoti_real_store_2.png",
      caption: "Hiramoti Collection — Established 1987"
    },
    {
      year: "2012",
      badge_sub: "Evolution",
      tag: "The First Renovation • Showroom Evolution",
      title: "The First Renovation",
      description: "To serve our growing family of customers better, Hiramoti Collection underwent its first major showroom renovation in 2012. Modern retail displays, expanded clothing collections, and a refined shopping experience were introduced — while preserving the warmth, personal attention, and trust that defined the brand from day one.",
      quote: "Preserving our warmth while evolving to serve growing generations.",
      image: "assets/images/hiramoti_store_interior.jpg",
      caption: "Showroom Transformation — 2012"
    },
    {
      year: "2026",
      badge_sub: "New Chapter",
      tag: "The Second Renovation • A New Chapter",
      title: "The Second Renovation",
      description: "In 2026, Hiramoti Collection unveiled a grand, state-of-the-art showroom renovation. Featuring contemporary lighting, premium display sections for suits, sherwanis, jackets, and everyday essentials, and an elevated shopping ambiance — designed to serve the next generation while honouring the legacy of the past.",
      quote: "Honouring the past. Building for the future.",
      image: "assets/images/hiramoti_exterior_entrance.jpg",
      caption: "The New Hiramoti Collection Showroom — 2026"
    }
  ]
};

async function loadFounderAdminData() {
  try {
    const res = await fetch("/api/admin/founder");
    if (res.ok) {
      const data = await res.json();
      if (data && data.founder) {
        cachedFounderData = data;
      }
    }
  } catch (err) {
    console.warn("Could not load /api/admin/founder:", err);
  }

  // Populate Founder Fields
  const f = cachedFounderData.founder || {};
  const nameEl = document.getElementById("founder-name");
  const desigEl = document.getElementById("founder-designation");
  const photoHidden = document.getElementById("founder-photo-hidden");
  const photoLabel = document.getElementById("founder-photo-filename-label");
  const photoThumb = document.getElementById("founder-photo-thumb");
  const quoteEl = document.getElementById("founder-quote");
  const bioEl = document.getElementById("founder-biography");

  if (nameEl) nameEl.value = f.name || "Late Shri Ujwal Rathi";
  if (desigEl) desigEl.value = f.designation || "Founder, Hiramoti Collection";
  var currentPhoto = (f.photo && !f.photo.includes("hiramoti_founder_home.jpg")) ? f.photo : "";
  if (photoHidden) photoHidden.value = currentPhoto;
  if (photoLabel) photoLabel.textContent = currentPhoto || "No photo uploaded (Using Commemorative Memorial Seal)";
  if (photoThumb) {
    if (currentPhoto) {
      photoThumb.src = resolveImageUrl(currentPhoto);
      photoThumb.style.objectFit = "cover";
      photoThumb.style.padding = "0";
    } else {
      photoThumb.src = "../assets/images/favicon.png";
      photoThumb.style.objectFit = "contain";
      photoThumb.style.padding = "12px";
      photoThumb.style.background = "#20040A";
    }
  }
  if (quoteEl) quoteEl.value = f.quote || "Trust is not given — it is earned, stitch by stitch, customer by customer.";
  if (bioEl) bioEl.value = f.biography || "";

  renderAdminMilestones(cachedFounderData.milestones || []);
}

function renderAdminMilestones(milestones) {
  const container = document.getElementById("milestones-admin-container");
  if (!container) return;

  container.innerHTML = "";
  milestones.forEach((m, idx) => {
    const card = document.createElement("div");
    card.className = "milestone-admin-card";
    card.style = "background: rgba(255,255,255,0.03); border: 1px solid var(--color-border-dark); border-radius: 8px; padding: 18px; position: relative;";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid var(--color-border-dark); padding-bottom: 8px;">
        <h4 style="font-family: var(--font-serif); font-size: 1.15rem; color: var(--color-gold); margin: 0;">
          Milestone #${idx + 1} — ${m.year || "New"}
        </h4>
        <button type="button" class="btn btn-outline-danger btn-xs" onclick="removeMilestone(${idx})">
          Remove
        </button>
      </div>

      <div class="form-row-2">
        <div class="form-group">
          <label>Milestone Year *</label>
          <input type="text" class="form-control ms-year" value="${m.year || ''}" placeholder="e.g. 1987" required>
        </div>
        <div class="form-group">
          <label>Badge Subtitle</label>
          <input type="text" class="form-control ms-badge-sub" value="${m.badge_sub || ''}" placeholder="e.g. Origin / Evolution / New Chapter">
        </div>
      </div>

      <div class="form-row-2">
        <div class="form-group">
          <label>Tag / Subtitle *</label>
          <input type="text" class="form-control ms-tag" value="${m.tag || ''}" placeholder="e.g. The Beginning • Vision • Trust">
        </div>
        <div class="form-group">
          <label>Milestone Title *</label>
          <input type="text" class="form-control ms-title" value="${m.title || ''}" placeholder="e.g. The Beginning">
        </div>
      </div>

      <div class="form-group">
        <label>Description *</label>
        <textarea class="form-control ms-desc" rows="3" placeholder="Milestone history details...">${m.description || ''}</textarea>
      </div>

      <div class="form-group">
        <label>Milestone Quote / Highlight (Optional)</label>
        <input type="text" class="form-control ms-quote" value="${m.quote || ''}" placeholder="e.g. Honouring the past. Building for the future.">
      </div>

      <!-- Milestone Device Image Upload -->
      <div class="form-group media-upload-group">
        <label>Milestone Image & Caption</label>
        <input type="file" id="ms-file-${idx}" accept="image/jpeg,image/png,image/webp" style="display: none;" onchange="handleMilestoneImageFileSelect(event, ${idx})">
        <input type="hidden" class="ms-image-hidden" id="ms-image-hidden-${idx}" value="${m.image || 'assets/images/hiramoti_store_interior.jpg'}">

        <div class="media-upload-action-row" style="margin-bottom: 8px;">
          <button type="button" class="btn btn-outline-gold btn-xs" onclick="document.getElementById('ms-file-${idx}').click()">
            📁 Choose Image from Device
          </button>
          <span id="ms-filename-${idx}" class="media-file-info text-muted" style="font-size: 0.76rem;">${m.image || 'Default'}</span>
        </div>

        <div style="display: flex; gap: 12px; align-items: center; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
          <img id="ms-thumb-${idx}" src="${resolveImageUrl(m.image || 'assets/images/hiramoti_store_interior.jpg')}" alt="Preview" style="width: 70px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid var(--color-gold-border);">
          <div style="flex: 1;">
            <input type="text" class="form-control ms-caption" value="${m.caption || ''}" placeholder="Image caption (e.g. Showroom Transformation — 2012)" style="font-size: 0.8rem; padding: 6px 10px;">
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function addNewMilestoneForm() {
  const container = document.getElementById("milestones-admin-container");
  if (!container) return;

  // Gather existing from DOM
  gatherMilestonesFromDOM();

  // Append new empty milestone
  cachedFounderData.milestones.push({
    year: "2026",
    badge_sub: "Milestone",
    tag: "Milestone Tag",
    title: "Milestone Title",
    description: "Milestone historical narrative...",
    quote: "",
    image: "assets/images/hiramoti_store_interior.jpg",
    caption: "Hiramoti Collection"
  });

  renderAdminMilestones(cachedFounderData.milestones);
  showToast("New milestone added. Remember to click Save Changes.", "info");
}

function removeMilestone(index) {
  openConfirmModal(
    "Remove Milestone",
    "Are you sure you want to remove this milestone from the timeline? You will need to click 'Save Founder Changes' to finalize.",
    () => {
      gatherMilestonesFromDOM();
      cachedFounderData.milestones.splice(index, 1);
      renderAdminMilestones(cachedFounderData.milestones);
      showToast("Milestone removed from list", "info");
    },
    "Remove Milestone"
  );
}

function handleFounderPhotoFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  const validExts = ["jpg", "jpeg", "png", "webp"];
  const ext = file.name.split(".").pop().toLowerCase();
  if (!validExts.includes(ext)) {
    showToast(`Invalid image format (.${ext}). Allowed: .jpg, .jpeg, .png, .webp`, "danger");
    e.target.value = "";
    return;
  }

  // Local preview
  const localUrl = URL.createObjectURL(file);
  const thumb = document.getElementById("founder-photo-thumb");
  if (thumb) thumb.src = localUrl;

  const label = document.getElementById("founder-photo-filename-label");
  if (label) label.textContent = `Selected: ${file.name} (Uploading...)`;

  const badge = document.getElementById("founder-photo-badge");
  if (badge) {
    badge.textContent = "Uploading...";
    badge.className = "badge-cover-source";
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("media_type", "image");

  fetch("/api/admin/upload-media", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success && data.url) {
        document.getElementById("founder-photo-hidden").value = data.url;
        if (label) label.textContent = `Uploaded: ${file.name}`;
        if (badge) {
          badge.textContent = "Uploaded Device Photo";
          badge.className = "badge-cover-source badge-uploaded";
        }
        if (thumb) thumb.src = resolveImageUrl(data.url);
        showToast("Founder photo uploaded successfully!", "success");
      } else {
        showToast(data.error || "Upload failed", "danger");
        if (label) label.textContent = "Upload failed — try again";
      }
    })
    .catch(err => {
      showToast("Network error uploading photo", "danger");
      if (label) label.textContent = "Upload failed";
    });
}

function resetFounderPhoto() {
  document.getElementById("founder-photo-hidden").value = "";
  const label = document.getElementById("founder-photo-filename-label");
  if (label) label.textContent = "No photo uploaded (Using Commemorative Memorial Seal)";
  const thumb = document.getElementById("founder-photo-thumb");
  if (thumb) {
    thumb.src = "../assets/images/favicon.png";
    thumb.style.objectFit = "contain";
    thumb.style.padding = "12px";
    thumb.style.background = "#20040A";
  }
  const badge = document.getElementById("founder-photo-badge");
  if (badge) {
    badge.textContent = "Memorial Seal";
    badge.className = "badge-cover-source";
  }
  showToast("Founder photo set to Memorial Seal", "info");
}

function handleMilestoneImageFileSelect(e, idx) {
  const file = e.target.files[0];
  if (!file) return;

  const localUrl = URL.createObjectURL(file);
  const thumb = document.getElementById(`ms-thumb-${idx}`);
  if (thumb) thumb.src = localUrl;

  const label = document.getElementById(`ms-filename-${idx}`);
  if (label) label.textContent = `Uploading ${file.name}...`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("media_type", "image");

  fetch("/api/admin/upload-media", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success && data.url) {
        const hidden = document.getElementById(`ms-image-hidden-${idx}`);
        if (hidden) hidden.value = data.url;
        if (label) label.textContent = `Uploaded: ${file.name}`;
        if (thumb) thumb.src = resolveImageUrl(data.url);
        showToast(`Milestone #${idx + 1} image uploaded!`, "success");
      } else {
        showToast(data.error || "Upload failed", "danger");
      }
    })
    .catch(err => {
      showToast("Network error uploading milestone image", "danger");
    });
}

function gatherMilestonesFromDOM() {
  const cards = document.querySelectorAll(".milestone-admin-card");
  const milestones = [];

  cards.forEach((card, i) => {
    const year = card.querySelector(".ms-year") ? card.querySelector(".ms-year").value.trim() : "";
    const badgeSub = card.querySelector(".ms-badge-sub") ? card.querySelector(".ms-badge-sub").value.trim() : "";
    const tag = card.querySelector(".ms-tag") ? card.querySelector(".ms-tag").value.trim() : "";
    const title = card.querySelector(".ms-title") ? card.querySelector(".ms-title").value.trim() : "";
    const desc = card.querySelector(".ms-desc") ? card.querySelector(".ms-desc").value.trim() : "";
    const quote = card.querySelector(".ms-quote") ? card.querySelector(".ms-quote").value.trim() : "";
    const imageHidden = card.querySelector(".ms-image-hidden") ? card.querySelector(".ms-image-hidden").value.trim() : "";
    const caption = card.querySelector(".ms-caption") ? card.querySelector(".ms-caption").value.trim() : "";

    milestones.push({
      year: year || "1987",
      badge_sub: badgeSub || "Milestone",
      tag: tag || "",
      title: title || "Milestone",
      description: desc || "",
      quote: quote || "",
      image: imageHidden || "assets/images/hiramoti_store_interior.jpg",
      caption: caption || ""
    });
  });

  cachedFounderData.milestones = milestones;
}

async function saveFounderData() {
  gatherMilestonesFromDOM();

  const name = document.getElementById("founder-name").value.trim();
  const designation = document.getElementById("founder-designation").value.trim();
  const photo = document.getElementById("founder-photo-hidden").value.trim();
  const quote = document.getElementById("founder-quote").value.trim();
  const biography = document.getElementById("founder-biography").value.trim();

  if (!name) {
    showToast("Please provide founder full name", "danger");
    return;
  }

  const payload = {
    founder: {
      name,
      designation,
      photo: photo || "assets/images/hiramoti_founder_home.jpg",
      quote,
      quote_author: name,
      biography
    },
    milestones: cachedFounderData.milestones
  };

  const alertEl = document.getElementById("founder-alert");
  if (alertEl) alertEl.style.display = "none";

  try {
    const res = await fetch("/api/admin/founder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (res.ok && result.success) {
      cachedFounderData = payload;
      showToast("Founder & Legacy content saved successfully!", "success");
      if (alertEl) {
        alertEl.textContent = "Changes saved! The public Founder & Legacy page has been updated.";
        alertEl.style.display = "block";
        setTimeout(() => { alertEl.style.display = "none"; }, 5000);
      }
    } else {
      showToast(result.error || "Failed to save founder changes", "danger");
    }
  } catch (err) {
    showToast("Network error saving founder changes", "danger");
  }
}

