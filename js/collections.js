/**
 * Hiramoti Collection, Satara — Dynamic Catalog, Multi-Level Filters & Sorting
 */

let activeCategory = "all";
let activeSubtype = "all";
let activeSort = "featured";
let searchQuery = "";
let selectedProductForModal = null;

document.addEventListener("DOMContentLoaded", () => {
  initUrlParams();
  initFilterControls();
  renderProducts();
  initQuickViewModal();
});

function initUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const catParam = params.get("category");
  const subParam = params.get("subtype");
  const qParam = params.get("q");

  if (catParam) activeCategory = catParam;
  if (subParam) activeSubtype = subParam;
  if (qParam) {
    searchQuery = qParam;
    const searchInput = document.getElementById("catalog-search-input");
    if (searchInput) searchInput.value = qParam;
  }
}

function initFilterControls() {
  // Category buttons
  const catPills = document.querySelectorAll(".category-pill");
  catPills.forEach(pill => {
    pill.addEventListener("click", () => {
      catPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeCategory = pill.dataset.category;
      activeSubtype = "all"; // Reset subtype when main category changes
      updateSubtypePills();
      renderProducts();
    });
  });

  // Search input with debounce
  const searchInput = document.getElementById("catalog-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.trim().toLowerCase();
      renderProducts();
    });
  }

  // Sort dropdown
  const sortSelect = document.getElementById("sort-by-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      activeSort = e.target.value;
      renderProducts();
    });
  }

  updateSubtypePills();
}

function updateSubtypePills() {
  const container = document.getElementById("subtype-pills-container");
  if (!container) return;

  // Filter subtypes according to activeCategory
  const availableSubtypes = SUBTYPES.filter(sub => {
    if (sub.id === "all") return true;
    if (activeCategory === "all") return true;
    return sub.category === activeCategory;
  });

  container.innerHTML = availableSubtypes.map(sub => `
    <button 
      class="filter-pill ${sub.id === activeSubtype ? "active" : ""}" 
      data-subtype="${sub.id}"
    >
      ${sub.name}
    </button>
  `).join("");

  container.querySelectorAll(".filter-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      container.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeSubtype = pill.dataset.subtype;
      renderProducts();
    });
  });
}

function renderProducts() {
  const grid = document.getElementById("products-catalog-grid");
  const countEl = document.getElementById("results-count-label");
  if (!grid) return;

  // Filtering
  let results = PRODUCTS_DATA.filter(product => {
    // Category match
    if (activeCategory !== "all" && product.category !== activeCategory) return false;
    // Subtype match
    if (activeSubtype !== "all" && product.subtype !== activeSubtype) return false;
    // Search query match
    if (searchQuery) {
      const matchName = product.name.toLowerCase().includes(searchQuery);
      const matchDesc = product.description.toLowerCase().includes(searchQuery);
      const matchFabric = product.fabric.toLowerCase().includes(searchQuery);
      const matchMarathi = product.marathi.toLowerCase().includes(searchQuery);
      const matchSubtype = product.subtype.toLowerCase().includes(searchQuery);
      if (!matchName && !matchDesc && !matchFabric && !matchMarathi && !matchSubtype) {
        return false;
      }
    }
    return true;
  });

  // Sorting
  if (activeSort === "price-low") {
    results.sort((a, b) => a.price - b.price);
  } else if (activeSort === "price-high") {
    results.sort((a, b) => b.price - a.price);
  } else if (activeSort === "rating") {
    results.sort((a, b) => b.rating - a.rating);
  } else if (activeSort === "reels") {
    results.sort((a, b) => (b.isReelHighlight ? 1 : 0) - (a.isReelHighlight ? 1 : 0));
  }

  // Update counter
  if (countEl) {
    countEl.innerText = `Showing ${results.length} royal styles in Satara store`;
  }

  if (results.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-16 text-center">
        <div class="w-16 h-16 rounded-full bg-[rgba(212,175,55,0.15)] border border-[#d4af37] flex items-center justify-center mx-auto mb-4 text-[#d4af37]">
          <i data-lucide="search-x" class="w-8 h-8"></i>
        </div>
        <h3 class="text-xl font-bold font-playfair text-[#f5e296] mb-2">No matching clothing found</h3>
        <p class="text-white/60 text-sm max-w-md mx-auto mb-6">Try clearing your filters or search keywords. You can also chat directly on WhatsApp to ask about custom orders in our Satara showroom.</p>
        <button onclick="resetFilters()" class="btn-gold px-6 py-2.5 rounded-full text-xs">Reset All Filters</button>
      </div>
    `;
    if (window.initLucide) window.initLucide();
    return;
  }

  grid.innerHTML = results.map(p => `
    <div class="royal-card group flex flex-col justify-between" data-product-id="${p.id}">
      <div>
        <!-- Card Image Header -->
        <div class="relative overflow-hidden aspect-[4/5] bg-black/40">
          <img 
            src="${p.image}" 
            alt="${p.name}" 
            loading="lazy"
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
          >
          
          <!-- Badges -->
          <div class="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
            ${p.badge ? `<span class="badge-gold">${p.badge}</span>` : ""}
            ${p.isReelHighlight ? `
              <span class="bg-gradient-to-r from-pink-600 to-rose-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-lg">
                <i data-lucide="play" class="w-2.5 h-2.5 fill-white"></i> Reel Viral
              </span>
            ` : ""}
          </div>

          <div class="absolute top-3 right-3 z-10">
            <span class="bg-black/75 backdrop-blur-md text-[#f5e296] text-xs font-bold px-2.5 py-1 rounded-full border border-[rgba(212,175,55,0.3)]">
              ${p.discount}
            </span>
          </div>

          <!-- Quick Action Overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4 gap-2">
            <button 
              onclick="openQuickView('${p.id}')"
              class="flex-1 bg-white/95 text-[#120b0c] hover:bg-[#d4af37] font-bold py-2 rounded-lg text-xs transition flex items-center justify-center gap-1.5 shadow-lg"
            >
              <i data-lucide="eye" class="w-3.5 h-3.5"></i> Quick View
            </button>
            ${p.reelId ? `
              <button 
                onclick="openReelById('${p.reelId}')"
                class="bg-pink-600/90 text-white hover:bg-pink-500 p-2 rounded-lg transition shadow-lg"
                title="Watch Instagram Reel"
              >
                <i data-lucide="play-circle" class="w-4 h-4"></i>
              </button>
            ` : ""}
          </div>
        </div>

        <!-- Card Content -->
        <div class="p-4">
          <div class="flex items-center justify-between text-xs text-white/50 mb-1">
            <span class="uppercase tracking-wider font-semibold text-[#d4af37]">${p.subtype.replace("_", " ")}</span>
            <div class="flex items-center gap-1 text-amber-400 font-bold">
              <i data-lucide="star" class="w-3 h-3 fill-amber-400"></i> ${p.rating}
            </div>
          </div>

          <h4 class="font-bold text-base text-white group-hover:text-[#f5e296] transition line-clamp-1 mb-0.5 font-playfair">
            ${p.name}
          </h4>
          <p class="text-xs text-[#d4af37]/80 font-medium mb-2 font-serif">${p.marathi}</p>

          <p class="text-xs text-white/70 line-clamp-2 mb-3 leading-relaxed">
            ${p.description}
          </p>

          <!-- Available Sizes -->
          <div class="flex items-center gap-1.5 flex-wrap mb-3">
            <span class="text-[11px] text-white/40">Sizes:</span>
            ${p.sizes.slice(0, 4).map(s => `
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/80 font-mono">${s}</span>
            `).join("")}
            ${p.sizes.length > 4 ? `<span class="text-[10px] text-white/40">+${p.sizes.length - 4}</span>` : ""}
          </div>
        </div>
      </div>

      <!-- Price & Order Action -->
      <div class="p-4 pt-0 border-t border-[rgba(212,175,55,0.15)] flex items-center justify-between mt-auto">
        <div>
          <div class="flex items-baseline gap-1.5">
            <span class="text-lg font-extrabold text-[#f5e296]">₹${p.price.toLocaleString("en-IN")}</span>
            <span class="text-xs text-white/40 line-through">₹${p.originalPrice.toLocaleString("en-IN")}</span>
          </div>
          <span class="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
            <i data-lucide="check-circle" class="w-2.5 h-2.5"></i> In Satara Store
          </span>
        </div>

        <button 
          onclick="openWhatsAppInquiry('${p.id}')"
          class="btn-whatsapp px-3.5 py-2 rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-md"
        >
          <i data-lucide="message-circle" class="w-3.5 h-3.5"></i>
          Order
        </button>
      </div>
    </div>
  `).join("");

  if (window.initLucide) window.initLucide();
}

function resetFilters() {
  activeCategory = "all";
  activeSubtype = "all";
  searchQuery = "";
  activeSort = "featured";

  const searchInput = document.getElementById("catalog-search-input");
  if (searchInput) searchInput.value = "";

  const catPills = document.querySelectorAll(".category-pill");
  catPills.forEach(p => {
    if (p.dataset.category === "all") p.classList.add("active");
    else p.classList.remove("active");
  });

  updateSubtypePills();
  renderProducts();
}

// Quick View Modal
function initQuickViewModal() {
  const modal = document.getElementById("product-quick-view-modal");
  const closeBtn = document.getElementById("quick-view-close-btn");
  if (!modal) return;

  if (closeBtn) closeBtn.addEventListener("click", closeQuickView);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeQuickView();
  });
}

function openQuickView(productId) {
  const product = PRODUCTS_DATA.find(p => p.id === productId);
  const modal = document.getElementById("product-quick-view-modal");
  if (!product || !modal) return;

  selectedProductForModal = product;

  document.getElementById("qv-image").src = product.image;
  document.getElementById("qv-title").innerText = product.name;
  document.getElementById("qv-marathi").innerText = product.marathi;
  document.getElementById("qv-price").innerText = `₹${product.price.toLocaleString("en-IN")}`;
  document.getElementById("qv-original-price").innerText = `₹${product.originalPrice.toLocaleString("en-IN")}`;
  document.getElementById("qv-discount").innerText = product.discount;
  document.getElementById("qv-fabric").innerText = product.fabric;
  document.getElementById("qv-description").innerText = product.description;

  // Render sizes
  const sizesContainer = document.getElementById("qv-sizes-container");
  if (sizesContainer) {
    sizesContainer.innerHTML = product.sizes.map((s, idx) => `
      <button class="px-3 py-1.5 rounded-lg border text-xs font-semibold ${idx === 0 ? "border-[#d4af37] bg-[#d4af37]/20 text-[#f5e296]" : "border-white/20 text-white/80 hover:border-[#d4af37]"}">
        ${s}
      </button>
    `).join("");
  }

  // Render colors
  const colorsContainer = document.getElementById("qv-colors-container");
  if (colorsContainer) {
    colorsContainer.innerHTML = product.colors.map(c => `
      <span class="text-xs px-2.5 py-1 rounded-full bg-white/10 text-white/90 border border-white/15">${c}</span>
    `).join("");
  }

  // WhatsApp CTA
  const orderBtn = document.getElementById("qv-whatsapp-btn");
  if (orderBtn) {
    orderBtn.onclick = () => openWhatsAppInquiry(product.id);
  }

  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";

  if (window.initLucide) window.initLucide();
}

function closeQuickView() {
  const modal = document.getElementById("product-quick-view-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "";
}

function openReelById(reelId) {
  const idx = REELS_DATA.findIndex(r => r.id === reelId);
  if (idx !== -1 && window.openReelsModal) {
    window.openReelsModal(idx);
  }
}

window.openQuickView = openQuickView;
window.closeQuickView = closeQuickView;
window.openReelById = openReelById;
window.resetFilters = resetFilters;
