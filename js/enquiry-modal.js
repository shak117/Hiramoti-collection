/**
 * Hiramoti Collection, Satara — Premium Customer Enquiry & Lead Modal
 * Handles customer enquiry submissions, product context attachment,
 * duplicate submission protection, backend persistence, and optional WhatsApp redirection.
 */

(function () {
  "use strict";

  const API_BASE = (window.location.protocol === "file:" || (!window.location.host.includes(":5000") && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || !window.location.port)))
    ? "http://localhost:5000"
    : "";

  let currentProductContext = null;
  let currentSource = "Website Enquiry";
  let isSubmitting = false;

  // ---------------------------------------------------------------------------
  // 1. INJECT MODAL MARKUP IF NOT PRESENT
  // ---------------------------------------------------------------------------
  function ensureModalExists() {
    if (document.getElementById("hm-enquiry-modal")) return;

    const modalHtml = `
      <div id="hm-enquiry-modal" class="hm-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="hm-enq-title">
        <div class="hm-modal-dialog">
          
          <!-- Header -->
          <div class="hm-modal-header">
            <div>
              <div class="hm-badge-gold">Powai Naka, Satara • Estd. 1987</div>
              <h3 id="hm-enq-title" class="hm-modal-title">Enquiry &amp; Style Consultation</h3>
            </div>
            <button type="button" class="hm-modal-close" onclick="window.closeEnquiryModal()" aria-label="Close enquiry modal">&times;</button>
          </div>

          <!-- Body -->
          <div class="hm-modal-body">
            
            <!-- Alert banner for errors -->
            <div id="hm-enq-error" class="hm-alert-error" style="display: none;"></div>

            <!-- SUCCESS VIEW (Hidden initially) -->
            <div id="hm-enq-success-card" class="hm-success-card" style="display: none;">
              <div class="hm-success-icon">✓</div>
              <h4 class="hm-success-title">Enquiry Submitted Successfully!</h4>
              <p class="hm-success-desc">
                Thank you, <strong id="hm-success-customer-name"></strong>! Our Hiramoti Collection team will contact you shortly.
              </p>
              
              <div id="hm-success-summary" class="hm-success-summary-box"></div>

              <div class="hm-success-actions">
                <a id="hm-success-wa-btn" href="#" target="_blank" rel="noopener" class="btn btn-whatsapp" style="width: 100%; justify-content: center; padding: 12px; font-weight: 700;">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 6px;"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.699c.971.53 1.83.81 2.802.81 3.181 0 5.767-2.587 5.768-5.766.001-3.182-2.586-5.768-5.774-5.768zm7.391 5.766c-.001 4.075-3.316 7.39-7.391 7.39-1.282 0-2.485-.333-3.535-.916l-4.148 1.088 1.107-4.045c-.682-1.12-1.045-2.417-1.045-3.517 0-4.076 3.315-7.391 7.391-7.391 4.076 0 7.392 3.315 7.392 7.391z"/></svg>
                  Open WhatsApp (Optional)
                </a>
                <button type="button" class="btn btn-outline" style="width: 100%; justify-content: center; margin-top: 8px;" onclick="window.closeEnquiryModal()">
                  Done
                </button>
              </div>
            </div>

            <!-- FORM VIEW -->
            <form id="hm-enquiry-form" name="enquiry" method="POST" action="/api/leads" onsubmit="window.submitEnquiryForm(event)" novalidate autocomplete="on">
              
              <!-- Product Context Preview Chip (Shown only when initiated from a product) -->
              <div id="hm-product-preview-box" class="hm-product-chip" style="display: none;">
                <div class="hm-product-chip-img-box">
                  <img id="hm-product-chip-img" src="" alt="Product Preview" onerror="this.src='assets/images/real_store_shirts.jpg';">
                </div>
                <div class="hm-product-chip-info">
                  <span class="hm-chip-badge">Selected Garment</span>
                  <h4 id="hm-product-chip-title" class="hm-chip-title"></h4>
                  <div class="hm-chip-meta">
                    <span id="hm-product-chip-category"></span>
                    <strong id="hm-product-chip-price" style="color: #d4af37;"></strong>
                    <span id="hm-product-chip-discount" class="hm-chip-discount"></span>
                  </div>
                </div>
              </div>

              <!-- Customer Details Row -->
              <div class="hm-form-row">
                <div class="hm-form-group">
                  <label class="hm-form-label" for="hm-enq-name">Full Name <span class="hm-req">*</span></label>
                  <input
                    type="text"
                    id="hm-enq-name"
                    name="name"
                    class="hm-form-input"
                    placeholder="e.g. Rahul Patil"
                    required
                    autocomplete="name"
                    autocapitalize="words"
                    spellcheck="false"
                  >
                </div>
                <div class="hm-form-group">
                  <label class="hm-form-label" for="hm-enq-phone">Mobile Number <span class="hm-req">*</span></label>
                  <input
                    type="tel"
                    id="hm-enq-phone"
                    name="phone"
                    class="hm-form-input"
                    placeholder="e.g. 98220 12345 (10 digits)"
                    required
                    autocomplete="tel"
                    inputmode="tel"
                  >
                </div>
              </div>

              <div class="hm-form-row">
                <div class="hm-form-group">
                  <label class="hm-form-label" for="hm-enq-email">Email Address <span style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">(Optional)</span></label>
                  <input
                    type="email"
                    id="hm-enq-email"
                    name="email"
                    class="hm-form-input"
                    placeholder="e.g. rahul@example.com"
                    autocomplete="email"
                    inputmode="email"
                    spellcheck="false"
                  >
                </div>
                <div class="hm-form-group">
                  <label class="hm-form-label" for="hm-enq-pref-contact">Preferred Contact Method</label>
                  <select id="hm-enq-pref-contact" name="preferred_contact" class="hm-form-select">
                    <option value="WhatsApp" selected>WhatsApp Message</option>
                    <option value="Phone Call">Phone Call</option>
                    <option value="Any">Either WhatsApp or Call</option>
                  </select>
                </div>
              </div>

              <!-- Product / Category of Interest -->
              <div class="hm-form-group" id="hm-interest-container">
                <label class="hm-form-label" for="hm-enq-category">Product / Category of Interest</label>
                <select id="hm-enq-category" name="category" class="hm-form-select">
                  <option value="All Collections">General Store Enquiry</option>
                  <option value="Bomber & TPU Jackets">Bomber &amp; TPU Jackets</option>
                  <option value="Cotton & Printed Shirts">Cotton &amp; Printed Shirts</option>
                  <option value="T-Shirt Combos (3 for ₹800)">T-Shirt &amp; Track Combos (3 for ₹800)</option>
                  <option value="Branded Denim & Trousers">Branded Denim &amp; Trousers</option>
                  <option value="Festive & Wedding Ethnic">Festive &amp; Wedding Ethnic Wear</option>
                  <option value="TechnoSport (10% OFF)">TechnoSport Collection (10% OFF)</option>
                  <option value="Hosiery Collection (10% OFF)">Hosiery Collection (10% OFF)</option>
                </select>
              </div>

              <!-- Message / Requirement -->
              <div class="hm-form-group">
                <label class="hm-form-label" for="hm-enq-message">Message / Requirement <span style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">(Optional)</span></label>
                <textarea id="hm-enq-message" name="message" class="hm-form-textarea" rows="2" placeholder="Tell us about size preferences, fitting requirements, or specific styles you'd like to check..."></textarea>
              </div>

              <!-- Hidden context fields -->
              <input type="hidden" id="hm-enq-product-id" name="product_id" value="">
              <input type="hidden" id="hm-enq-product-name" name="product_name" value="">
              <input type="hidden" id="hm-enq-price" name="price" value="">
              <input type="hidden" id="hm-enq-product-url" name="product_url" value="">
              <input type="hidden" id="hm-enq-source" name="source" value="Website Enquiry">

              <!-- Submit Button -->
              <button type="submit" id="hm-enq-submit-btn" class="btn btn-hero-gold hm-submit-btn" style="width: 100%; justify-content: center; padding: 13px; font-weight: 700;">
                <span id="hm-enq-btn-text">Submit Enquiry</span>
                <svg id="hm-enq-btn-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-left: 6px;"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
              
              <p class="hm-form-footer-note">
                🔒 Your contact details are safely encrypted and directly handled by our Powai Naka showroom desk.
              </p>
            </form>

          </div>
        </div>
      </div>
    `;

    const div = document.createElement("div");
    div.innerHTML = modalHtml;
    document.body.appendChild(div.firstElementChild);

    // Close on backdrop click
    const modalEl = document.getElementById("hm-enquiry-modal");
    if (modalEl) {
      modalEl.addEventListener("click", function (e) {
        if (e.target === modalEl) {
          window.closeEnquiryModal();
        }
      });
    }

    // Close on ESC key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modalEl && modalEl.classList.contains("active")) {
        window.closeEnquiryModal();
      }
    });

    // Auto-clear error alerts on input or browser autofill change
    ["hm-enq-name", "hm-enq-phone", "hm-enq-email"].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        const clearErr = () => {
          const errBox = document.getElementById("hm-enq-error");
          if (errBox && errBox.style.display !== "none") {
            errBox.style.display = "none";
            errBox.textContent = "";
          }
        };
        el.addEventListener("input", clearErr);
        el.addEventListener("change", clearErr);
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 2. OPEN & CLOSE MODAL HANDLERS
  // ---------------------------------------------------------------------------
  window.openEnquiryModal = function (productContext = null, source = null) {
    ensureModalExists();

    currentProductContext = productContext;
    currentSource = source || (productContext ? "Product Enquiry" : determinePageSource());

    const modal = document.getElementById("hm-enquiry-modal");
    const form = document.getElementById("hm-enquiry-form");
    const successCard = document.getElementById("hm-enq-success-card");
    const errorBox = document.getElementById("hm-enq-error");

    if (errorBox) {
      errorBox.style.display = "none";
      errorBox.textContent = "";
    }

    if (form) form.style.display = "block";
    if (successCard) successCard.style.display = "none";

    // Reset button state
    setButtonLoading(false);

    // Populate or clear product context preview
    const previewBox = document.getElementById("hm-product-preview-box");
    const previewImg = document.getElementById("hm-product-chip-img");
    const previewTitle = document.getElementById("hm-product-chip-title");
    const previewCat = document.getElementById("hm-product-chip-category");
    const previewPrice = document.getElementById("hm-product-chip-price");
    const previewDisc = document.getElementById("hm-product-chip-discount");

    const hiddenId = document.getElementById("hm-enq-product-id");
    const hiddenName = document.getElementById("hm-enq-product-name");
    const hiddenPrice = document.getElementById("hm-enq-price");
    const hiddenUrl = document.getElementById("hm-enq-product-url");
    const hiddenSource = document.getElementById("hm-enq-source");
    const selectCat = document.getElementById("hm-enq-category");

    if (productContext && (productContext.name || productContext.id)) {
      if (previewBox) previewBox.style.display = "flex";
      if (previewImg) previewImg.src = productContext.image || "assets/images/real_store_shirts.jpg";
      if (previewTitle) previewTitle.textContent = productContext.name || "Garment Enquiry";
      if (previewCat) previewCat.textContent = productContext.category ? `[${productContext.category}]` : "";
      if (previewPrice) previewPrice.textContent = productContext.price ? (String(productContext.price).startsWith("₹") ? productContext.price : `₹${productContext.price}`) : "";
      if (previewDisc) previewDisc.textContent = productContext.discount || "";

      if (hiddenId) hiddenId.value = productContext.id || "";
      if (hiddenName) hiddenName.value = productContext.name || "";
      if (hiddenPrice) hiddenPrice.value = productContext.price || "";
      if (hiddenUrl) hiddenUrl.value = window.location.href;
      if (hiddenSource) hiddenSource.value = currentSource;
    } else {
      if (previewBox) previewBox.style.display = "none";
      if (hiddenId) hiddenId.value = "";
      if (hiddenName) hiddenName.value = "General Enquiry";
      if (hiddenPrice) hiddenPrice.value = "";
      if (hiddenUrl) hiddenUrl.value = window.location.href;
      if (hiddenSource) hiddenSource.value = currentSource;
    }

    if (modal) {
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    // Auto-focus name field
    setTimeout(() => {
      const nameInput = document.getElementById("hm-enq-name");
      if (nameInput) nameInput.focus();
    }, 150);
  };

  window.closeEnquiryModal = function () {
    const modal = document.getElementById("hm-enquiry-modal");
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";
    }
  };

  // Helper to open modal for a specific product by ID
  window.openProductEnquiry = function (productId) {
    let p = null;
    if (window.REAL_PRODUCTS && window.REAL_PRODUCTS.length) {
      p = window.REAL_PRODUCTS.find(item => item.id === productId);
    }
    if (!p && window.PRODUCTS_DATA && window.PRODUCTS_DATA.length) {
      p = window.PRODUCTS_DATA.find(item => item.id === productId);
    }

    if (p) {
      window.openEnquiryModal({
        id: p.id,
        name: p.name,
        category: p.category,
        price: p.price,
        discount: p.discount,
        image: p.image
      }, "Catalogue Product Card");
    } else {
      window.openEnquiryModal({ id: productId, name: `Product (${productId})` }, "Product Enquiry");
    }
  };

  function determinePageSource() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes("collections")) return "Catalogue Enquiry";
    if (path.includes("catalog")) return "Offers Enquiry";
    if (path.includes("contact")) return "Contact Page Enquiry";
    if (path.includes("about")) return "About Page Enquiry";
    if (path.includes("reels")) return "Reels Page Enquiry";
    if (path.includes("gallery")) return "Gallery Enquiry";
    if (path.includes("founder")) return "Founder Page Enquiry";
    return "Homepage Enquiry";
  }

  // ---------------------------------------------------------------------------
  // 3. SUBMIT ENQUIRY FORM (With Duplicate Protection & Validation)
  // ---------------------------------------------------------------------------
  window.submitEnquiryForm = async function (e) {
    if (e) e.preventDefault();

    if (isSubmitting) return;

    const errorBox = document.getElementById("hm-enq-error");
    if (errorBox) {
      errorBox.style.display = "none";
      errorBox.textContent = "";
    }

    const form = document.getElementById("hm-enquiry-form");
    const nameInput = document.getElementById("hm-enq-name");
    const phoneInput = document.getElementById("hm-enq-phone");
    const emailInput = document.getElementById("hm-enq-email");
    const prefContactInput = document.getElementById("hm-enq-pref-contact");
    const categorySelect = document.getElementById("hm-enq-category");
    const messageInput = document.getElementById("hm-enq-message");

    const hiddenId = document.getElementById("hm-enq-product-id");
    const hiddenName = document.getElementById("hm-enq-product-name");
    const hiddenPrice = document.getElementById("hm-enq-price");
    const hiddenUrl = document.getElementById("hm-enq-product-url");
    const hiddenSource = document.getElementById("hm-enq-source");

    // Read directly from DOM input values, falling back to form.elements (guarantees reading browser-autofilled values)
    const name = ((nameInput ? nameInput.value : "") || (form && form.elements["name"] ? form.elements["name"].value : "")).trim();
    const phoneRaw = ((phoneInput ? phoneInput.value : "") || (form && form.elements["phone"] ? form.elements["phone"].value : "")).trim();
    const email = ((emailInput ? emailInput.value : "") || (form && form.elements["email"] ? form.elements["email"].value : "")).trim();
    const prefContact = ((prefContactInput ? prefContactInput.value : "") || (form && form.elements["preferred_contact"] ? form.elements["preferred_contact"].value : "WhatsApp")).trim();
    const message = ((messageInput ? messageInput.value : "") || (form && form.elements["message"] ? form.elements["message"].value : "")).trim();

    // Client Validation
    if (!name || name.length < 2) {
      showError("Please enter your full name (at least 2 characters).");
      if (nameInput) nameInput.focus();
      return;
    }

    // Phone normalization & validation for Indian numbers
    // Accommodates Chrome Autofill variations (+91, spaces, 0, dashes, brackets)
    let cleanedDigits = phoneRaw.replace(/[^0-9]/g, "");
    if (cleanedDigits.startsWith("0091")) {
      cleanedDigits = cleanedDigits.substring(4);
    } else if (cleanedDigits.length === 12 && cleanedDigits.startsWith("91")) {
      cleanedDigits = cleanedDigits.substring(2);
    } else if (cleanedDigits.length === 11 && cleanedDigits.startsWith("0")) {
      cleanedDigits = cleanedDigits.substring(1);
    } else if (cleanedDigits.length > 10) {
      const last10 = cleanedDigits.slice(-10);
      if (/^[6-9]\d{9}$/.test(last10)) {
        cleanedDigits = last10;
      }
    }

    const validPhone = cleanedDigits;
    if (!validPhone || validPhone.length !== 10 || !/^[6-9]/.test(validPhone)) {
      showError("Please enter a valid 10-digit mobile number (e.g. 98220 12345).");
      if (phoneInput) phoneInput.focus();
      return;
    }

    // Normal email validation - accepts valid emails, rejects invalid text (e.g. pawawarsh)
    if (email && !/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/.test(email)) {
      showError("Please enter a valid email address.");
      if (emailInput) emailInput.focus();
      return;
    }

    let productId = hiddenId ? hiddenId.value : "";
    let productName = hiddenName ? hiddenName.value : "";
    let category = categorySelect ? categorySelect.value : "General";
    let price = hiddenPrice ? hiddenPrice.value : "";

    if (currentProductContext) {
      productId = currentProductContext.id || productId;
      productName = currentProductContext.name || productName;
      category = currentProductContext.category || category;
      price = currentProductContext.price ? String(currentProductContext.price) : price;
    }

    if (!productName || productName === "General Enquiry") {
      productName = category || "General Enquiry";
    }

    // Set duplicate prevention state
    setButtonLoading(true);

    const payload = {
      name: name,
      phone: validPhone,
      email: email,
      product_id: productId,
      product_name: productName,
      category: category,
      price: price,
      product_url: hiddenUrl ? hiddenUrl.value : window.location.href,
      message: message,
      preferred_contact: prefContact,
      source: hiddenSource ? hiddenSource.value : currentSource,
      page_url: window.location.href
    };

    try {
      const response = await fetch(`${API_BASE}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Success: Show confirmation card with optional WhatsApp button
        showSuccessView({
          leadId: data.lead_id,
          name: name,
          phone: validPhone,
          interest: productName,
          category: category,
          message: message
        });

        // Reset form inputs for next time
        if (document.getElementById("hm-enquiry-form")) {
          document.getElementById("hm-enquiry-form").reset();
        }
      } else {
        // Server validation error
        setButtonLoading(false);
        showError(data.error || "Unable to submit your enquiry. Please try again.");
      }
    } catch (err) {
      console.error("Enquiry submission error:", err);
      setButtonLoading(false);
      showError("Unable to submit your enquiry. Please check your network and try again.");
    }
  };

  function setButtonLoading(loading) {
    isSubmitting = loading;
    const btn = document.getElementById("hm-enq-submit-btn");
    const btnText = document.getElementById("hm-enq-btn-text");
    const btnIcon = document.getElementById("hm-enq-btn-icon");

    if (!btn) return;

    if (loading) {
      btn.disabled = true;
      btn.style.opacity = "0.75";
      btn.style.cursor = "not-allowed";
      if (btnText) btnText.textContent = "Submitting Enquiry...";
      if (btnIcon) btnIcon.style.display = "none";
    } else {
      btn.disabled = false;
      btn.style.opacity = "1";
      btn.style.cursor = "pointer";
      if (btnText) btnText.textContent = "Submit Enquiry";
      if (btnIcon) btnIcon.style.display = "inline-block";
    }
  }

  function showError(msg) {
    const errorBox = document.getElementById("hm-enq-error");
    if (errorBox) {
      errorBox.textContent = msg;
      errorBox.style.display = "block";
    }
  }

  function showSuccessView(leadInfo) {
    const form = document.getElementById("hm-enquiry-form");
    const successCard = document.getElementById("hm-enq-success-card");
    const customerNameEl = document.getElementById("hm-success-customer-name");
    const summaryBox = document.getElementById("hm-success-summary");
    const waBtn = document.getElementById("hm-success-wa-btn");

    if (form) form.style.display = "none";
    if (successCard) successCard.style.display = "block";

    if (customerNameEl) customerNameEl.textContent = leadInfo.name;

    if (summaryBox) {
      summaryBox.innerHTML = `
        <div style="font-size: 0.85rem; line-height: 1.6; color: #fff;">
          <div><strong style="color: #d4af37;">Lead Reference:</strong> #L-${leadInfo.leadId}</div>
          <div><strong style="color: #d4af37;">Interest:</strong> ${leadInfo.interest}</div>
          <div><strong style="color: #d4af37;">Phone:</strong> +91 ${leadInfo.phone}</div>
          ${leadInfo.message ? `<div><strong style="color: #d4af37;">Note:</strong> "${leadInfo.message}"</div>` : ''}
        </div>
      `;
    }

    // Configure optional WhatsApp secondary action
    if (waBtn) {
      const waText = `Hello Hiramoti Collection,\nI have submitted an enquiry regarding *${leadInfo.interest}*.\nMy name is ${leadInfo.name}. Please share details and availability.`;
      waBtn.href = `https://wa.me/919595989815?text=${encodeURIComponent(waText)}`;
    }
  }

  // ---------------------------------------------------------------------------
  // 4. AUTO-WIRE ENQUIRY BUTTONS SITE-WIDE
  // ---------------------------------------------------------------------------
  function autoWireEnquiryButtons() {
    ensureModalExists();

    // Wire all buttons that say "Enquiry" or have specific classes
    document.querySelectorAll("button, a").forEach(el => {
      const txt = (el.textContent || "").trim();
      const isEnquiryBtn = txt === "Enquiry" || el.classList.contains("header-cta") || el.classList.contains("footer-book-btn") || (el.classList.contains("btn-hero-glass") && txt === "Enquiry");

      if (isEnquiryBtn) {
        el.dataset.enquiryBound = "true";
        el.removeAttribute("onclick");
        el.onclick = function (e) {
          if (e) {
            e.preventDefault();
            e.stopPropagation();
          }
          window.openEnquiryModal();
          return false;
        };
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoWireEnquiryButtons);
  } else {
    autoWireEnquiryButtons();
  }

  // Periodic check for dynamically rendered buttons (e.g. products rendered after API fetch)
  setInterval(() => {
    autoWireEnquiryButtons();
    document.querySelectorAll(".btn-card-enquire").forEach(btn => {
      if (!btn.dataset.enquiryBound) {
        btn.dataset.enquiryBound = "true";
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          const card = btn.closest(".ecommerce-product-card");
          if (card) {
            const titleEl = card.querySelector(".product-title");
            const priceEl = card.querySelector(".product-sale-price");
            const imgEl = card.querySelector("img");
            const brandEl = card.querySelector(".product-brand-name");
            window.openEnquiryModal({
              name: titleEl ? titleEl.textContent.trim() : "Garment",
              price: priceEl ? priceEl.textContent.trim() : "",
              category: brandEl ? brandEl.textContent.trim() : "Catalogue",
              image: imgEl ? imgEl.src : ""
            }, "Catalogue Product Card");
          } else {
            window.openEnquiryModal();
          }
        });
      }
    });
  }, 500);

})();
