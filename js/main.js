/**
 * Hiramoti Collection, Satara — Global JavaScript & Navigation
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initMobileMenu();
  initWhatsAppFloating();
  initLucide();
  initAudioAmbient();
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function initNavbar() {
  const navbar = document.getElementById("main-navbar");
  if (!navbar) return;

  window.addEventListener("scroll", () => {
    if (window.scrollY > 40) {
      navbar.classList.add("bg-[#120b0ce6]", "backdrop-blur-md", "shadow-xl", "border-b", "border-[rgba(212,175,55,0.25)]");
      navbar.classList.remove("bg-transparent");
    } else {
      navbar.classList.remove("bg-[#120b0ce6]", "backdrop-blur-md", "shadow-xl", "border-b", "border-[rgba(212,175,55,0.25)]");
      navbar.classList.add("bg-transparent");
    }
  });
}

function initMobileMenu() {
  const menuBtn = document.getElementById("mobile-menu-btn");
  const drawer = document.getElementById("mobile-drawer");
  const closeBtn = document.getElementById("close-drawer-btn");
  const overlay = document.getElementById("drawer-overlay");

  if (!menuBtn || !drawer) return;

  const openDrawer = () => {
    drawer.classList.add("open");
    if (overlay) overlay.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  };

  const closeDrawer = () => {
    drawer.classList.remove("open");
    if (overlay) overlay.classList.add("hidden");
    document.body.style.overflow = "";
  };

  menuBtn.addEventListener("click", openDrawer);
  if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
  if (overlay) overlay.addEventListener("click", closeDrawer);
}

function initWhatsAppFloating() {
  const btn = document.getElementById("whatsapp-float-btn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const text = encodeURIComponent(
      `Hello Hiramoti Collection Satara! I am visiting your website and would like to inquire about your latest clothing collections & store offers at Powai Naka.`
    );
    window.open(`https://wa.me/${STORE_CONFIG.whatsapp}?text=${text}`, "_blank");
  });
}

// Royal Ambient Theme Audio Synthesizer (Shehnai / Festive Drone simulation)
let audioCtx = null;
let isAudioPlaying = false;
let ambientOsc = null;
let gainNode = null;

function initAudioAmbient() {
  const audioBtn = document.getElementById("ambient-audio-toggle");
  if (!audioBtn) return;

  audioBtn.addEventListener("click", () => {
    if (!isAudioPlaying) {
      startAmbientTune();
      audioBtn.innerHTML = `
        <i data-lucide="volume-2" class="w-4 h-4 text-[#d4af37]"></i>
        <span class="text-xs font-semibold text-[#f5e296] hidden sm:inline">Music: On</span>
      `;
      isAudioPlaying = true;
    } else {
      stopAmbientTune();
      audioBtn.innerHTML = `
        <i data-lucide="volume-x" class="w-4 h-4 text-[#d4af37]/60"></i>
        <span class="text-xs font-semibold text-[#d4af37]/60 hidden sm:inline">Music: Off</span>
      `;
      isAudioPlaying = false;
    }
    initLucide();
  });
}

function startAmbientTune() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === "suspended") audioCtx.resume();

    // Create warm royal drone chord (Tanpura/Harmonium aesthetic)
    gainNode = audioCtx.createGain();
    gainNode.gain.setValueAtTime(0.001, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.08, audioCtx.currentTime + 2);
    gainNode.connect(audioCtx.destination);

    // Fundamental frequencies for royal Raag Yaman (C#, G#, C#)
    const freqs = [138.59, 207.65, 277.18, 311.13];
    freqs.forEach(freq => {
      const osc = audioCtx.createOscillator();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      osc.connect(gainNode);
      osc.start();
    });
  } catch (e) {
    console.warn("Audio ambient not supported:", e);
  }
}

function stopAmbientTune() {
  if (gainNode && audioCtx) {
    gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1);
    setTimeout(() => {
      if (audioCtx) audioCtx.close();
      audioCtx = null;
    }, 1000);
  }
}

// Global helper: direct WhatsApp product inquiry
function openWhatsAppInquiry(productId) {
  const product = PRODUCTS_DATA.find(p => p.id === productId);
  if (!product) return;

  const msg = encodeURIComponent(
    `Hello Hiramoti Collection Satara! 👑\n` +
    `I am interested in buying: *${product.name}* (Code: ${product.id})\n` +
    `Price: ₹${product.price}\n` +
    `Category: ${product.category} - ${product.subtype}\n` +
    `Please share available sizes and delivery or store pickup options at Powai Naka.`
  );
  window.open(`https://wa.me/${STORE_CONFIG.whatsapp}?text=${msg}`, "_blank");
}

window.openWhatsAppInquiry = openWhatsAppInquiry;
window.initLucide = initLucide;
