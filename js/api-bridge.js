/**
 * Hiramoti Collection, Satara — Dynamic Database & API Integration Bridge
 * Fetches live products, stock, prices, and reels from the backend database.
 * Automatically synchronizes public pages and provides seamless offline fallback.
 */

(function () {
  "use strict";

  // Fetch live products and reels on page initialization
  document.addEventListener("DOMContentLoaded", function () {
    fetchLiveProducts();
    fetchLiveReels();
    interceptAppointmentForms();
  });

  function resolvePublicImageUrl(url) {
    if (!url) return "assets/images/real_reel_DaiL4H0zCqV.jpg";
    const trimmed = String(url).trim();
    if (trimmed.startsWith("http://") || trimmed.startsWith("https://") || trimmed.startsWith("data:")) {
      return trimmed;
    }
    if (trimmed.startsWith("/")) {
      return trimmed.replace(/^\/+/, "");
    }
    return trimmed;
  }

  // ---------------------------------------------------------------------------
  // 1. LIVE PRODUCTS SYNC
  // ---------------------------------------------------------------------------
  async function fetchLiveProducts() {
    try {
      const res = await fetch("/api/products?_t=" + Date.now(), { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.products && data.products.length > 0) {
        // Map database products into matching shape for front-end
        window.REAL_PRODUCTS = data.products.map(p => ({
          id: p.id,
          name: p.name,
          marathi: p.marathi_name || "",
          category: p.category,
          subtype: p.subtype,
          price: p.price,
          originalPrice: p.original_price || (p.price * 1.5),
          discount: p.discount || "",
          badge: p.badge || (p.stock <= 0 ? "Out of Stock" : "In Stock"),
          image: p.image,
          reelUrl: p.reel_url || "https://www.instagram.com/hiramoticollection/",
          description: p.description || "",
          sizes: p.sizes_list || ["M", "L", "XL"],
          stock: p.stock,
          status: p.status
        }));
        window.PRODUCTS_DATA = window.REAL_PRODUCTS;

        // Trigger dynamic re-render on Collections page if present
        if (typeof window.renderRealCatalog === "function") {
          const params = new URLSearchParams(window.location.search);
          const currentCat = params.get("category") || "all";
          window.renderRealCatalog(currentCat);
        }

        document.dispatchEvent(new CustomEvent("hiramoti:products-updated", {
          detail: { products: window.REAL_PRODUCTS }
        }));
      }
    } catch (err) {
      console.log("API Bridge: Falling back to local catalog data.");
    }
  }

  // ---------------------------------------------------------------------------
  // 2. LIVE REELS SYNC
  // ---------------------------------------------------------------------------
  async function fetchLiveReels() {
    try {
      const res = await fetch("/api/reels?_t=" + Date.now(), { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.reels && data.reels.length > 0) {
        window.REELS_DATA = data.reels.map(r => ({
          id: r.id,
          code: r.code || "",
          url: r.url,
          embedUrl: r.embed_url,
          title: r.title,
          marathi: r.marathi_title || "",
          caption: r.caption || "",
          price: r.price || "SPECIAL OFFER",
          offer: r.offer || "VIRAL DROP",
          category: r.category || "general",
          image: r.image,
          displayOrder: r.display_order
        }));

        // Dynamically update home page & reels hub grids
        updatePublicReelsGrids(window.REELS_DATA);

        document.dispatchEvent(new CustomEvent("hiramoti:reels-updated", {
          detail: { reels: window.REELS_DATA }
        }));
      }
    } catch (err) {
      console.log("API Bridge: Falling back to local reels data.");
    }
  }

  function updatePublicReelsGrids(reels) {
    // 1. Home Page Reels Grid (.reels-grid in index.html)
    const homeReelsGrid = document.querySelector("#reels-section .reels-grid");
    if (homeReelsGrid) {
      homeReelsGrid.innerHTML = reels.map((r, idx) => `
        <div class="reel-box">
          <div class="reel-media-wrapper" onclick="openReelEmbed('${r.embedUrl}')">
            <img src="${resolvePublicImageUrl(r.image)}" alt="${r.title}" onerror="this.onerror=null; this.src='assets/images/real_reel_DaiL4H0zCqV.jpg';">
            <span class="reel-badge-top">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
              Reel ${idx + 1}
            </span>
            <span class="reel-price-badge">${r.price}</span>
            <div class="reel-play-btn-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            </div>
            <div class="reel-play-overlay">
              <span style="font-size: 0.72rem; color: var(--color-gold-light); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">${r.offer}</span>
              <h4 style="font-size: 1rem; font-weight: 700; color: #fff;">${r.title}</h4>
            </div>
          </div>
          <div class="reel-info">
            <h4 class="reel-title">${r.title}</h4>
            <p class="reel-caption">${r.caption}</p>
            <div class="reel-actions">
              <button onclick="openReelEmbed('${r.embedUrl}')" class="btn btn-outline-gold">
                Watch Reel
              </button>
              <a href="https://wa.me/919595989815?text=${encodeURIComponent("Hello Hiramoti Collection Satara! I saw your Reel: " + r.title + " (" + r.price + "). Please share details.")}" target="_blank" rel="noopener" class="btn btn-whatsapp">
                Order ${r.price}
              </a>
            </div>
          </div>
        </div>
      `).join("");
    }

    // 2. Reels Hub Grid (.reels-grid in reels.html)
    const reelsHubGrid = document.querySelector("main .reels-grid");
    if (reelsHubGrid && window.location.pathname.includes("reels")) {
      reelsHubGrid.innerHTML = reels.map((r, idx) => `
        <div class="reel-box" style="border: 1.5px solid var(--color-gold-border); border-radius: var(--radius-md); overflow: hidden; background: rgba(38, 5, 13, 0.9); box-shadow: var(--shadow-sm); display: flex; flex-direction: column;">
          <div class="reel-media-wrapper" onclick="openReelEmbed('${r.embedUrl}')" style="position: relative; aspect-ratio: 9/14; overflow: hidden; cursor: pointer; background: #000;">
            <img src="${resolvePublicImageUrl(r.image)}" alt="${r.title}" onerror="this.onerror=null; this.src='assets/images/real_reel_DaiL4H0zCqV.jpg';" style="width: 100%; height: 100%; object-fit: cover;">
            <span class="reel-badge-top" style="position: absolute; top: 12px; left: 12px; background: rgba(0,0,0,0.7); color: #fff; padding: 4px 10px; border-radius: var(--radius-full); font-size: 0.72rem; font-weight: 700; border: 1px solid rgba(212,175,55,0.4);">
              Drop ${idx + 1}
            </span>
            <span class="reel-price-badge" style="position: absolute; top: 12px; right: 12px; background: var(--color-burgundy-light); color: var(--color-gold-light); padding: 4px 10px; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 700; border: 1px solid var(--color-gold);">
              ${r.price}
            </span>
            <div class="reel-play-btn-center" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 50px; height: 50px; border-radius: 50%; background: rgba(212,175,55,0.85); color: #1a0308; display: flex; align-items: center; justify-content: center;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            </div>
          </div>
          <div class="reel-info" style="padding: 18px; display: flex; flex-direction: column; flex: 1;">
            <h4 style="font-family: var(--font-serif); font-size: 1.15rem; color: var(--color-gold-pale); margin-bottom: 6px;">${r.title}</h4>
            <p style="font-size: 0.8rem; color: rgba(255,255,255,0.75); line-height: 1.45; margin-bottom: 16px; flex: 1;">${r.caption}</p>
            <div style="display: flex; gap: 8px; margin-top: auto;">
              <button onclick="openReelEmbed('${r.embedUrl}')" class="btn btn-outline-gold" style="flex: 1; padding: 7px 10px; font-size: 0.78rem;">
                Watch
              </button>
              <a href="https://wa.me/919595989815?text=${encodeURIComponent("Hello Hiramoti Collection Satara! I saw Reel Drop: " + r.title + ". Please share details.")}" target="_blank" rel="noopener" class="btn btn-whatsapp" style="flex: 1; padding: 7px 10px; font-size: 0.78rem;">
                Enquire
              </a>
            </div>
          </div>
        </div>
      `).join("");
    }

    // Attach modal video helper
    interceptReelModalPlayer();
  }

  // ---------------------------------------------------------------------------
  // Universal Reel Player Support (Video Files & Instagram Embeds)
  // ---------------------------------------------------------------------------
  function interceptReelModalPlayer() {
    const origOpenReelEmbed = window.openReelEmbed;
    window.openReelEmbed = function (embedUrl) {
      const reelModal = document.getElementById("reel-embed-modal");
      const reelIframe = document.getElementById("reel-iframe");
      if (!reelModal) {
        if (typeof origOpenReelEmbed === "function") return origOpenReelEmbed(embedUrl);
        return;
      }

      let reelVideo = document.getElementById("reel-video-player");
      if (!reelVideo) {
        reelVideo = document.createElement("video");
        reelVideo.id = "reel-video-player";
        reelVideo.controls = true;
        reelVideo.playsInline = true;
        reelVideo.style.width = "100%";
        reelVideo.style.maxHeight = "540px";
        reelVideo.style.borderRadius = "8px";
        reelVideo.style.background = "#000";
        reelVideo.style.display = "none";
        if (reelIframe && reelIframe.parentNode) {
          reelIframe.parentNode.appendChild(reelVideo);
        }
      }

      const isVideo = embedUrl && (embedUrl.endsWith(".mp4") || embedUrl.endsWith(".webm") || embedUrl.endsWith(".mov") || embedUrl.includes("uploads/hm_vid"));

      if (isVideo) {
        if (reelIframe) {
          reelIframe.src = "";
          reelIframe.style.display = "none";
        }
        if (reelVideo) {
          reelVideo.src = resolvePublicImageUrl(embedUrl);
          reelVideo.style.display = "block";
          reelVideo.play().catch(() => {});
        }
      } else {
        if (reelVideo) {
          reelVideo.pause();
          reelVideo.src = "";
          reelVideo.style.display = "none";
        }
        if (reelIframe) {
          reelIframe.src = embedUrl;
          reelIframe.style.display = "block";
        }
      }

      reelModal.classList.add("active");
      document.body.style.overflow = "hidden";
    };

    const closeReel = document.getElementById("close-reel-modal");
    if (closeReel) {
      closeReel.addEventListener("click", function () {
        const reelVideo = document.getElementById("reel-video-player");
        if (reelVideo) {
          reelVideo.pause();
          reelVideo.src = "";
          reelVideo.style.display = "none";
        }
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 3. APPOINTMENT BOOKINGS DATABASE INTERCEPT
  // ---------------------------------------------------------------------------
  function interceptAppointmentForms() {
    const originalSubmit = window.submitAppointmentForm;
    window.submitAppointmentForm = function (e) {
      if (e) e.preventDefault();

      const nameInput = document.getElementById("apt-name");
      const phoneInput = document.getElementById("apt-phone");
      const areaInput = document.getElementById("apt-address");
      const dateInput = document.getElementById("apt-date");
      const timeInput = document.getElementById("apt-time");
      const notesInput = document.getElementById("apt-notes");

      const name = nameInput ? nameInput.value.trim() : "";
      const phone = phoneInput ? phoneInput.value.trim() : "";
      const area = areaInput ? areaInput.value.trim() : "";
      const visit_date = dateInput ? dateInput.value : "";
      const time_slot = timeInput ? timeInput.value : "";
      const notes = notesInput ? notesInput.value.trim() : "";

      const checkedBoxes = document.querySelectorAll("input[name='clothing_interest']:checked");
      const interests = [];
      checkedBoxes.forEach(cb => interests.push(cb.value));

      if (name && phone) {
        // Send to backend database
        fetch("/api/enquiries", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: name,
            phone: phone,
            area: area,
            visit_date: visit_date,
            time_slot: time_slot,
            style_interest: interests.join(", ") || "General Collection",
            message: notes
          })
        }).catch(err => console.log("Appointment sync error:", err));
      }

      // Delegate to original WhatsApp redirect flow
      if (typeof originalSubmit === "function") {
        return originalSubmit.call(this, e);
      }
    };
  }

  // Expose API helpers
  window.HiramotiBridge = {
    fetchLiveProducts: fetchLiveProducts,
    fetchLiveReels: fetchLiveReels
  };
})();
