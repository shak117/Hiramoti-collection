/**
 * Hiramoti Collection, Satara — Instagram Reels Interactive Hub
 * Center of Attraction Feature: 9:16 Video Player, Likes, Sound & Direct WhatsApp Order
 */

let currentReelIndex = 0;
let isReelPlaying = true;
let isReelMuted = true;
let likedReels = new Set();

document.addEventListener("DOMContentLoaded", () => {
  initReelsHomeCarousel();
  initReelsGrid();
  initReelsModal();
});

// Render Home Page Reels Carousel
function initReelsHomeCarousel() {
  const container = document.getElementById("home-reels-carousel");
  if (!container) return;

  container.innerHTML = REELS_DATA.map((reel, idx) => `
    <div class="reel-card flex-shrink-0 w-[240px] sm:w-[280px]" data-reel-index="${idx}">
      <video 
        src="${reel.video}" 
        poster="${reel.poster}"
        muted 
        loop 
        playsinline
        preload="metadata"
        class="w-full h-full object-cover"
      ></video>
      <div class="reel-overlay">
        <div class="flex items-center justify-between">
          <span class="reel-badge">
            <i data-lucide="instagram" class="w-3.5 h-3.5 text-pink-400"></i>
            Reel
          </span>
          <span class="text-xs font-semibold text-white/90 bg-black/50 px-2 py-0.5 rounded-full flex items-center gap-1">
            <i data-lucide="eye" class="w-3 h-3 text-[#d4af37]"></i> ${reel.views}
          </span>
        </div>

        <div class="reel-play-btn">
          <i data-lucide="play" class="w-6 h-6 ml-1"></i>
        </div>

        <div>
          <div class="sound-bars mb-2">
            <span></span><span></span><span></span><span></span>
          </div>
          <h4 class="text-white font-bold text-sm line-clamp-1 mb-1 font-playfair">${reel.title}</h4>
          <p class="text-white/70 text-xs line-clamp-2">${reel.caption}</p>
          <div class="mt-2 flex items-center justify-between text-xs text-[#f5e296] font-semibold">
            <span class="flex items-center gap-1"><i data-lucide="heart" class="w-3.5 h-3.5 text-rose-500"></i> ${reel.likes}</span>
            <span class="text-xs uppercase text-[#d4af37] underline flex items-center gap-1">Watch & Shop <i data-lucide="arrow-right" class="w-3 h-3"></i></span>
          </div>
        </div>
      </div>
    </div>
  `).join("");

  if (window.initLucide) window.initLucide();

  // Attach hover-to-play preview and click-to-open
  const cards = container.querySelectorAll(".reel-card");
  cards.forEach(card => {
    const video = card.querySelector("video");
    const playBtn = card.querySelector(".reel-play-btn");

    card.addEventListener("mouseenter", () => {
      if (video) {
        video.play().catch(() => {});
        playBtn.style.opacity = "0";
      }
    });

    card.addEventListener("mouseleave", () => {
      if (video) {
        video.pause();
        video.currentTime = 0;
        playBtn.style.opacity = "1";
      }
    });

    card.addEventListener("click", () => {
      const idx = parseInt(card.dataset.reelIndex, 10);
      openReelsModal(idx);
    });
  });
}

// Render Dedicated Reels Page Grid
function initReelsGrid() {
  const grid = document.getElementById("reels-grid-container");
  if (!grid) return;

  renderReelsGrid(REELS_DATA);

  // Filter tabs on Reels page
  const tabBtns = document.querySelectorAll(".reel-filter-tab");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active", "bg-gradient-to-r", "from-[#d4af37]", "to-[#aa771c]", "text-[#120b0c]"));
      btn.classList.add("active", "bg-gradient-to-r", "from-[#d4af37]", "to-[#aa771c]", "text-[#120b0c]");
      
      const category = btn.dataset.category;
      if (category === "all") {
        renderReelsGrid(REELS_DATA);
      } else {
        const filtered = REELS_DATA.filter(r => r.category === category);
        renderReelsGrid(filtered);
      }
    });
  });
}

function renderReelsGrid(reels) {
  const grid = document.getElementById("reels-grid-container");
  if (!grid) return;

  grid.innerHTML = reels.map((reel) => {
    const originalIndex = REELS_DATA.findIndex(r => r.id === reel.id);
    return `
      <div class="reel-card" data-reel-index="${originalIndex}">
        <video 
          src="${reel.video}" 
          poster="${reel.poster}"
          muted 
          loop 
          playsinline
          preload="metadata"
          class="w-full h-full object-cover"
        ></video>
        <div class="reel-overlay">
          <div class="flex items-center justify-between">
            <span class="reel-badge">
              <i data-lucide="instagram" class="w-3.5 h-3.5 text-pink-400"></i>
              @hiramoticollection
            </span>
            <span class="text-xs font-semibold text-white/90 bg-black/60 px-2.5 py-1 rounded-full flex items-center gap-1">
              <i data-lucide="eye" class="w-3 h-3 text-[#d4af37]"></i> ${reel.views}
            </span>
          </div>

          <div class="reel-play-btn">
            <i data-lucide="play" class="w-6 h-6 ml-1"></i>
          </div>

          <div>
            <div class="sound-bars mb-2">
              <span></span><span></span><span></span><span></span>
            </div>
            <h4 class="text-white font-bold text-base mb-1 font-playfair">${reel.title}</h4>
            <p class="text-white/80 text-xs line-clamp-2 mb-2">${reel.caption}</p>
            <div class="flex items-center justify-between text-xs text-[#f5e296] font-semibold border-t border-white/10 pt-2">
              <span class="flex items-center gap-1.5"><i data-lucide="heart" class="w-3.5 h-3.5 text-rose-500 fill-rose-500"></i> ${reel.likes}</span>
              <button class="bg-[#d4af37] text-[#120b0c] px-3 py-1 rounded-full text-xs font-bold hover:bg-[#fae69e] transition flex items-center gap-1">
                Shop Reel <i data-lucide="shopping-bag" class="w-3 h-3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");

  if (window.initLucide) window.initLucide();

  // Attach hover-to-play & modal open
  const cards = grid.querySelectorAll(".reel-card");
  cards.forEach(card => {
    const video = card.querySelector("video");
    const playBtn = card.querySelector(".reel-play-btn");

    card.addEventListener("mouseenter", () => {
      if (video) {
        video.play().catch(() => {});
        playBtn.style.opacity = "0";
      }
    });

    card.addEventListener("mouseleave", () => {
      if (video) {
        video.pause();
        video.currentTime = 0;
        playBtn.style.opacity = "1";
      }
    });

    card.addEventListener("click", () => {
      const idx = parseInt(card.dataset.reelIndex, 10);
      openReelsModal(idx);
    });
  });
}

// Interactive Fullscreen Reel Viewer Modal
function initReelsModal() {
  const modal = document.getElementById("reels-viewer-modal");
  if (!modal) return;

  const closeBtn = document.getElementById("reel-modal-close");
  const prevBtn = document.getElementById("reel-prev-btn");
  const nextBtn = document.getElementById("reel-next-btn");
  const soundBtn = document.getElementById("reel-sound-toggle");
  const playPauseBtn = document.getElementById("reel-play-toggle");
  const likeBtn = document.getElementById("reel-like-btn");
  const shareBtn = document.getElementById("reel-share-btn");
  const video = document.getElementById("modal-reel-video");

  if (closeBtn) closeBtn.addEventListener("click", closeReelsModal);

  // Close when clicking backdrop
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeReelsModal();
  });

  // Prev / Next reel navigation
  if (prevBtn) prevBtn.addEventListener("click", () => navigateReel(-1));
  if (nextBtn) nextBtn.addEventListener("click", () => navigateReel(1));

  // Sound toggle
  if (soundBtn && video) {
    soundBtn.addEventListener("click", () => {
      isReelMuted = !isReelMuted;
      video.muted = isReelMuted;
      soundBtn.innerHTML = isReelMuted 
        ? `<i data-lucide="volume-x" class="w-5 h-5"></i>`
        : `<i data-lucide="volume-2" class="w-5 h-5 text-[#d4af37]"></i>`;
      if (window.initLucide) window.initLucide();
    });
  }

  // Play / Pause toggle
  if (playPauseBtn && video) {
    playPauseBtn.addEventListener("click", () => {
      togglePlayState();
    });
  }

  if (video) {
    video.addEventListener("click", () => {
      togglePlayState();
    });

    // Double tap/click to like
    let lastTap = 0;
    video.addEventListener("touchend", (e) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - lastTap;
      if (tapLength < 300 && tapLength > 0) {
        likeCurrentReel(e.clientX || 200, e.clientY || 300);
        e.preventDefault();
      }
      lastTap = currentTime;
    });

    video.addEventListener("dblclick", (e) => {
      likeCurrentReel(e.clientX, e.clientY);
    });

    // Progress bar update
    video.addEventListener("timeupdate", () => {
      const progressBar = document.getElementById("reel-progress-fill");
      if (progressBar && video.duration) {
        const pct = (video.currentTime / video.duration) * 100;
        progressBar.style.width = `${pct}%`;
      }
    });
  }

  // Like button
  if (likeBtn) {
    likeBtn.addEventListener("click", () => {
      likeCurrentReel();
    });
  }

  // Share button
  if (shareBtn) {
    shareBtn.addEventListener("click", () => {
      const reel = REELS_DATA[currentReelIndex];
      if (navigator.share) {
        navigator.share({
          title: reel.title,
          text: `Check out this reel by Hiramoti Collection Satara: ${reel.title}`,
          url: window.location.href,
        }).catch(() => {});
      } else {
        navigator.clipboard.writeText(window.location.href);
        alert("Reel link copied to clipboard!");
      }
    });
  }

  // Keyboard navigation
  window.addEventListener("keydown", (e) => {
    if (!modal.classList.contains("active")) return;
    if (e.key === "Escape") closeReelsModal();
    if (e.key === "ArrowUp" || e.key === "ArrowLeft") navigateReel(-1);
    if (e.key === "ArrowDown" || e.key === "ArrowRight") navigateReel(1);
    if (e.key === " ") {
      e.preventDefault();
      togglePlayState();
    }
    if (e.key === "m" || e.key === "M") {
      if (soundBtn) soundBtn.click();
    }
  });
}

function openReelsModal(index) {
  const modal = document.getElementById("reels-viewer-modal");
  if (!modal) return;

  currentReelIndex = (index + REELS_DATA.length) % REELS_DATA.length;
  modal.classList.add("active");
  document.body.style.overflow = "hidden";

  loadReelData(currentReelIndex);
}

function closeReelsModal() {
  const modal = document.getElementById("reels-viewer-modal");
  const video = document.getElementById("modal-reel-video");
  if (video) {
    video.pause();
    video.currentTime = 0;
  }
  if (modal) modal.classList.remove("active");
  document.body.style.overflow = "";
}

function navigateReel(direction) {
  currentReelIndex = (currentReelIndex + direction + REELS_DATA.length) % REELS_DATA.length;
  loadReelData(currentReelIndex);
}

function loadReelData(index) {
  const reel = REELS_DATA[index];
  const video = document.getElementById("modal-reel-video");
  const titleEl = document.getElementById("reel-modal-title");
  const captionEl = document.getElementById("reel-modal-caption");
  const audioEl = document.getElementById("reel-modal-audio");
  const likesCountEl = document.getElementById("reel-likes-count");
  const viewsCountEl = document.getElementById("reel-views-count");
  const shopDrawer = document.getElementById("reel-shop-drawer");
  const likeBtnIcon = document.getElementById("reel-like-icon");

  if (titleEl) titleEl.innerText = reel.title;
  if (captionEl) captionEl.innerText = reel.caption;
  if (audioEl) audioEl.innerText = reel.soundTitle;
  if (viewsCountEl) viewsCountEl.innerText = reel.views;

  const isLiked = likedReels.has(reel.id);
  if (likesCountEl) {
    likesCountEl.innerText = isLiked ? `${reel.likes} (Liked)` : reel.likes;
  }
  if (likeBtnIcon) {
    if (isLiked) {
      likeBtnIcon.classList.add("text-rose-500", "fill-rose-500");
    } else {
      likeBtnIcon.classList.remove("text-rose-500", "fill-rose-500");
    }
  }

  // Linked Product Drawer
  if (shopDrawer) {
    const product = PRODUCTS_DATA.find(p => p.id === reel.linkedProductId);
    if (product) {
      shopDrawer.innerHTML = `
        <div class="flex items-center gap-3 p-3 bg-[#1e0e12]/90 border border-[rgba(212,175,55,0.3)] rounded-xl backdrop-blur-md">
          <img src="${product.image}" class="w-14 h-14 rounded-lg object-cover border border-[#d4af37]/40 flex-shrink-0" alt="${product.name}">
          <div class="flex-1 min-w-0">
            <span class="text-[10px] text-[#f5e296] uppercase font-bold tracking-wider">Featured in this Reel</span>
            <h5 class="text-white text-xs font-bold truncate">${product.name}</h5>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-[#d4af37] font-bold text-sm">₹${product.price}</span>
              <span class="text-white/40 text-xs line-through">₹${product.originalPrice}</span>
            </div>
          </div>
          <button 
            onclick="openWhatsAppInquiry('${product.id}')"
            class="bg-gradient-to-r from-[#25D366] to-[#128C7E] text-white px-3 py-2 rounded-lg text-xs font-bold flex items-center gap-1 shadow-lg hover:brightness-110 flex-shrink-0"
          >
            <i data-lucide="message-circle" class="w-3.5 h-3.5"></i>
            Order
          </button>
        </div>
      `;
    } else {
      shopDrawer.innerHTML = "";
    }
  }

  if (video) {
    video.src = reel.video;
    video.poster = reel.poster;
    video.muted = isReelMuted;
    video.currentTime = 0;
    video.play().catch(err => {
      console.log("Autoplay prevented:", err);
    });
    isReelPlaying = true;
  }

  if (window.initLucide) window.initLucide();
}

function togglePlayState() {
  const video = document.getElementById("modal-reel-video");
  const playIcon = document.getElementById("reel-play-icon");
  if (!video) return;

  if (video.paused) {
    video.play();
    isReelPlaying = true;
    if (playIcon) playIcon.style.opacity = "0";
  } else {
    video.pause();
    isReelPlaying = false;
    if (playIcon) playIcon.style.opacity = "1";
  }
}

function likeCurrentReel(x, y) {
  const reel = REELS_DATA[currentReelIndex];
  likedReels.add(reel.id);

  const likesCountEl = document.getElementById("reel-likes-count");
  const likeBtnIcon = document.getElementById("reel-like-icon");

  if (likesCountEl) likesCountEl.innerText = `${reel.likes} (Liked)`;
  if (likeBtnIcon) {
    likeBtnIcon.classList.add("text-rose-500", "fill-rose-500", "scale-125");
    setTimeout(() => likeBtnIcon.classList.remove("scale-125"), 300);
  }

  // Floating heart effect on video screen
  const container = document.querySelector(".reel-modal-container");
  if (container) {
    const heart = document.createElement("div");
    heart.className = "floating-heart";
    heart.innerHTML = "❤️";
    heart.style.left = `${x ? x - container.getBoundingClientRect().left : container.clientWidth / 2}px`;
    heart.style.top = `${y ? y - container.getBoundingClientRect().top : container.clientHeight / 2}px`;
    container.appendChild(heart);
    setTimeout(() => heart.remove(), 1000);
  }
}

window.openReelsModal = openReelsModal;
window.closeReelsModal = closeReelsModal;
