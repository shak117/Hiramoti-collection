/**
 * Hiramoti Collection, Satara — Store & Real Instagram Social Data
 * Established 1987, Powai Naka, Satara
 * 100% Real Store Photography & Authentic Instagram Reels
 */

const STORE_CONFIG = {
  name: "Hiramoti Collection",
  marathiName: "हिरामोती कलेक्शन",
  tagline: "Satara's Royal Fashion Destination Since 1987",
  address: "Rajat Sagar Complex, Opposite Rajdhani Satara Selfie Point, Powai Naka, Satara – 415001",
  landmark: "Opp. Rajdhani Satara Selfie Point, Powai Naka",
  city: "Satara, Maharashtra",
  phone1: "9595989815",
  phone2: "7588745454",
  whatsapp: "919595989815",
  instagramUrl: "https://www.instagram.com/hiramoticollection/",
  instagramHandle: "@hiramoticollection",
  hours: "9:15 AM – 9:15 PM (Open All 7 Days)",
  establishedYear: 1987,
  yearsOfTrust: "39+",
};

// 8 Authentic Instagram Reels directly requested by client
const REELS_DATA = [
  {
    id: "reel-1",
    code: "DaiL4H0zCqV",
    url: "https://www.instagram.com/hiramoticollection/reel/DaiL4H0zCqV/",
    embedUrl: "https://www.instagram.com/reel/DaiL4H0zCqV/embed/",
    title: "Bomber Jacket Sale Live — Only ₹699/-",
    marathi: "बॉम्बर जॅकेट स्पेशल ऑफर — फक्त ₹६९९/-",
    caption: "Upgrade your wardrobe with latest Men’s & Women’s Bomber Jackets! Premium Quality, Trendy & Stylish Designs, Comfortable Fit. Rajatsagar Complex, Opp. Rajdhani Satara Selfie Point, Powai Naka.",
    price: "₹699",
    offer: "LIMITED DEAL",
    category: "jackets",
    image: "assets/images/real_reel_DaiL4H0zCqV.jpg",
    tags: ["#jackets", "#bomberjacket", "#mensfashion", "#satara", "#satarkar"]
  },
  {
    id: "reel-2",
    code: "DdQyFX4Tv4t",
    url: "https://www.instagram.com/hiramoticollection/reel/DdQyFX4Tv4t/",
    embedUrl: "https://www.instagram.com/reel/DdQyFX4Tv4t/embed/",
    title: "T-Shirt & Track Pant — ₹800 मध्ये 3!",
    marathi: "टी-शर्ट व ट्रॅक पँट — ₹८०० मध्ये ३!",
    caption: "काहीही घ्या — ₹800 मध्ये 3! गणेश उत्सव स्पेशल ऑफरचा फायदा घ्या आणि स्टाईलमध्ये साजरा करा बाप्पाचा उत्सव! Hiramoti Collection, Satara.",
    price: "₹800 for 3",
    offer: "FESTIVE OFFER",
    category: "casual",
    image: "assets/images/real_reel_DdQyFX4Tv4t.jpg",
    tags: ["#menswear", "#tshirts", "#trackpants", "#satarkar", "#trending"]
  },
  {
    id: "reel-3",
    code: "DdL4HYAzqZK",
    url: "https://www.instagram.com/hiramoticollection/reel/DdL4HYAzqZK/",
    embedUrl: "https://www.instagram.com/reel/DdL4HYAzqZK/embed/",
    title: "Favourite Shirts Restock Alert — ₹799/-",
    marathi: "फेव्हरेट शर्ट्स पुन्हा स्टॉक मध्ये — फक्त ₹७९९/-",
    caption: "SHIRT RESTOCK ALERT! तुमचा Favourite Shirt पुन्हा STOCK मध्ये! Trendy Look, Premium Feel, Limited Stock. Powai Naka Satara.",
    price: "₹799",
    offer: "RESTOCK HIT",
    category: "shirts",
    image: "assets/images/real_reel_DdL4HYAzqZK.jpg",
    tags: ["#satara", "#mensfashion", "#satarkar", "#menswear", "#shirt"]
  },
  {
    id: "reel-4",
    code: "DcqiOSIzvCQ",
    url: "https://www.instagram.com/hiramoticollection/reel/DcqiOSIzvCQ/",
    embedUrl: "https://www.instagram.com/reel/DcqiOSIzvCQ/embed/",
    title: "Branded Denim, Cotton & Checks Shirts",
    marathi: "ब्रँडेड डेनिम व कॉटन शर्ट्स — ₹७९९/-",
    caption: "BRANDED SHIRTS @ JUST ₹799/-! Denim, Cotton, Checks, Double Pocket. Size Available: M to 3XL. Best Quality • Premium Collection • Perfect Fit.",
    price: "₹799",
    offer: "SIZES M-3XL",
    category: "shirts",
    image: "assets/images/real_reel_DcqiOSIzvCQ.jpg",
    tags: ["#satarkar", "#mensfashion", "#doublepocket", "#denimshirt"]
  },
  {
    id: "reel-5",
    code: "Dcp2loUTRWp",
    url: "https://www.instagram.com/hiramoticollection/reel/Dcp2loUTRWp/",
    embedUrl: "https://www.instagram.com/reel/Dcp2loUTRWp/embed/",
    title: "TPU Weatherproof & Bomber Jacket @ ₹399/-",
    marathi: "टीपीयू व बॉम्बर जॅकेट महाबचत — ₹३९९/-",
    caption: "499/- चे TPU & BOMBER JACKET आता फक्त ₹399/- मध्ये! धमाकेदार ऑफर! आजच खरेदी करा आणि ₹100 ची बचत करा. Hiramoti Collection, Powai Naka.",
    price: "₹399",
    offer: "SAVE ₹100",
    category: "jackets",
    image: "assets/images/real_reel_Dcp2loUTRWp.jpg",
    tags: ["#tpujacket", "#bomberjacket", "#satara", "#menswear"]
  },
  {
    id: "reel-6",
    code: "Dcd2dn2NKZ9",
    url: "https://www.instagram.com/hiramoticollection/reel/Dcd2dn2NKZ9/",
    embedUrl: "https://www.instagram.com/reel/Dcd2dn2NKZ9/embed/",
    title: "Trendy Printed Half Shirts @ ₹799/-",
    marathi: "ट्रेंडी प्रिंटेड हाफ शर्ट्स — ₹७९९/-",
    caption: "TRENDY PRINTED HALF SHIRTS! Upgrade Your Style! Trendy Prints, Stylish & Comfortable. Pick Your Print, Rock Your Style. Available at Powai Naka Satara.",
    price: "₹799",
    offer: "MANY PRINTS",
    category: "shirts",
    image: "assets/images/real_reel_Dcd2dn2NKZ9.jpg",
    tags: ["#trendingshirt", "#printedshirts", "#menswear", "#satarkar"]
  },
  {
    id: "reel-7",
    code: "DcdL5uwTPTs",
    url: "https://www.instagram.com/hiramoticollection/reel/DcdL5uwTPTs/",
    embedUrl: "https://www.instagram.com/reel/DcdL5uwTPTs/embed/",
    title: "Designer Floral & Tropical Printed Shirts",
    marathi: "डिझायनर फ्लोरल व प्रिंटेड शर्ट्स",
    caption: "Rock Your Style! Hundreds of fresh prints in breathable pure cotton. Limited Stock — Grab Yours Now at Hiramoti Collection Satara.",
    price: "₹799",
    offer: "HOT SELLER",
    category: "shirts",
    image: "assets/images/real_reel_DcdL5uwTPTs.jpg",
    tags: ["#printshirt", "#shirt", "#menswear", "#mensfashion", "#satarkar"]
  },
  {
    id: "reel-8",
    code: "DcX8iP-zOb_",
    url: "https://www.instagram.com/hiramoticollection/reel/DcX8iP-zOb_/",
    embedUrl: "https://www.instagram.com/reel/DcX8iP-zOb_/embed/",
    title: "Imported Leather Jackets in 6 Colours",
    marathi: "इम्पोर्टेड लेदर जॅकेट्स (६ कलर्स)",
    caption: "IMPORTED LEATHER JACKET! Premium Imported Collection in 6 Stunning Colours. High Quality & Premium Finish. Choose Your Colour, Own Your Style!",
    price: "₹1,499",
    offer: "6 COLOURS",
    category: "jackets",
    image: "assets/images/real_reel_DcX8iP-zOb_.jpg",
    tags: ["#leatherjackets", "#jacket", "#fashionjacket", "#satara"]
  }
];

// Real Showroom Photography Gallery Items
const GALLERY_ITEMS = [
  {
    id: "gal-1",
    title: "Grand Showroom Interior & Glass Display Counters",
    subtitle: "Rajat Sagar Complex, Powai Naka Satara",
    category: "showroom",
    isWide: true,
    image: "assets/images/hiramoti_store_interior.jpg"
  },
  {
    id: "gal-2",
    title: "Full Stack Branded Cotton & Lycra Shirts Shelf",
    subtitle: "Over 500+ Shirt Designs in Stock",
    category: "shirts",
    isWide: false,
    image: "assets/images/real_store_shirts.jpg"
  },
  {
    id: "gal-3",
    title: "Premium Stretch Denim & Trousers Counter",
    subtitle: "Heavy Ring-Spun Denim Sizes 28 to 42",
    category: "jeans",
    isWide: false,
    image: "assets/images/real_store_jeans.jpg"
  },
  {
    id: "gal-4",
    title: "Central Shopping Aisles & Customer Trial Experience",
    subtitle: "Spacious boutique shopping at Powai Naka",
    category: "showroom",
    isWide: false,
    image: "assets/images/real_store_center.jpg"
  },
  {
    id: "gal-5",
    title: "Hiramoti Fashion Hub Display",
    subtitle: "Satara's Trusted Clothing Destination",
    category: "showroom",
    isWide: false,
    image: "assets/images/hiramoti_real_store_2.png"
  },
  {
    id: "gal-6",
    title: "Reversible & Bomber Jackets Rack",
    subtitle: "As Seen on Instagram Reel @hiramoticollection",
    category: "jackets",
    isWide: false,
    image: "assets/images/real_reel_DaiL4H0zCqV.jpg"
  },
  {
    id: "gal-7",
    title: "Imported Biker Leather Jackets in 6 Tones",
    subtitle: "Tan, Black, Olive, Wine & Navy",
    category: "jackets",
    isWide: false,
    image: "assets/images/real_reel_DcX8iP-zOb_.jpg"
  },
  {
    id: "gal-8",
    title: "Trendy Summer Printed Half Shirts Collection",
    subtitle: "Double-washed cotton for all-day comfort",
    category: "shirts",
    isWide: false,
    image: "assets/images/real_reel_Dcd2dn2NKZ9.jpg"
  }
];

// Product Catalog (Categories & Subtypes backed by Real Reel Items & Store Stock)
const REAL_PRODUCTS = [
  {
    id: "HM-JKT-01",
    name: "Dual-Tone Reversible Bomber Jacket",
    marathi: "रिव्हर्सिबल बॉम्बर जॅकेट",
    category: "mens",
    subtype: "jackets",
    price: 699,
    originalPrice: 1299,
    discount: "46% OFF",
    badge: "Viral Reel",
    image: "assets/images/real_reel_DaiL4H0zCqV.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DaiL4H0zCqV/",
    description: "Featured in our viral Instagram reel! Reversible 2-in-1 bomber jacket with storm-rib cuffs, brass zippers, and deep pockets.",
    sizes: ["M", "L", "XL", "XXL"]
  },
  {
    id: "HM-JKT-02",
    name: "TPU Weatherproof Windcheater Jacket",
    marathi: "टीपीयू ऑल-वेदर जॅकेट",
    category: "mens",
    subtype: "jackets",
    price: 399,
    originalPrice: 799,
    discount: "50% OFF",
    badge: "Mega Offer",
    image: "assets/images/real_reel_Dcp2loUTRWp.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/Dcp2loUTRWp/",
    description: "Special offer ₹399/- only! Wind and rain resistant TPU lightweight jacket, ideal for Satara rides and travel wear.",
    sizes: ["M", "L", "XL"]
  },
  {
    id: "HM-JKT-03",
    name: "Imported Premium Leather Jacket",
    marathi: "इम्पोर्टेड लेदर जॅकेट (६ कलर्स)",
    category: "mens",
    subtype: "jackets",
    price: 1499,
    originalPrice: 2499,
    discount: "40% OFF",
    badge: "Imported",
    image: "assets/images/real_reel_DcX8iP-zOb_.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DcX8iP-zOb_/",
    description: "Top-grade imported leather jacket available in 6 stunning shades. Premium metal hardware with satin inner lining.",
    sizes: ["M", "L", "XL", "XXL"]
  },
  {
    id: "HM-SHT-01",
    name: "Executive Cotton Double-Pocket Branded Shirt",
    marathi: "डबल पॉकेट कॉटन ब्रँडेड शर्ट",
    category: "mens",
    subtype: "formal_shirts",
    price: 799,
    originalPrice: 1299,
    discount: "38% OFF",
    badge: "Reel Bestseller",
    image: "assets/images/real_reel_DcqiOSIzvCQ.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DcqiOSIzvCQ/",
    description: "Available from M to 3XL! Heavy-duty pure cotton, structured collar, and utility double pockets.",
    sizes: ["M", "L", "XL", "XXL", "3XL"]
  },
  {
    id: "HM-SHT-02",
    name: "Signature Restocked Favourite Cotton Shirt",
    marathi: "फेव्हरेट कॉटन शर्ट री-स्टॉक",
    category: "mens",
    subtype: "formal_shirts",
    price: 799,
    originalPrice: 1199,
    discount: "33% OFF",
    badge: "Restocked",
    image: "assets/images/real_reel_DdL4HYAzqZK.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DdL4HYAzqZK/",
    description: "Satara's favorite shirt back in stock! Soft breathable fabric, wrinkle-resistant twill finish.",
    sizes: ["38", "40", "42", "44"]
  },
  {
    id: "HM-SHT-03",
    name: "Trendy Cuban-Collar Printed Half Shirt",
    marathi: "क्युबन कॉलर प्रिंटेड हाफ शर्ट",
    category: "mens",
    subtype: "party_wear",
    price: 799,
    originalPrice: 1299,
    discount: "38% OFF",
    badge: "Trending",
    image: "assets/images/real_reel_Dcd2dn2NKZ9.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/Dcd2dn2NKZ9/",
    description: "Hundreds of fresh prints! Relaxed holiday and party fit, double-washed pure cotton.",
    sizes: ["M", "L", "XL"]
  },
  {
    id: "HM-CAS-01",
    name: "Ganesh Utsav Combo: T-Shirt & Track Pant (3 for ₹800)",
    marathi: "टी-शर्ट व ट्रॅक पँट कॉम्बो (३ साठी ₹८००)",
    category: "mens",
    subtype: "casual_denim",
    price: 800,
    originalPrice: 1500,
    discount: "3 for ₹800",
    badge: "Festive Offer",
    image: "assets/images/real_reel_DdQyFX4Tv4t.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DdQyFX4Tv4t/",
    description: "Any 3 pieces of premium cotton round-neck t-shirts or four-way stretch track pants for just ₹800!",
    sizes: ["M", "L", "XL", "XXL"]
  },
  {
    id: "HM-SHT-04",
    name: "Tropical Summer Floral Party Shirt",
    marathi: "ट्रॉपिकल फ्लोरल पार्टी शर्ट",
    category: "mens",
    subtype: "party_wear",
    price: 799,
    originalPrice: 1199,
    discount: "33% OFF",
    badge: "Club Favorite",
    image: "assets/images/real_reel_DcdL5uwTPTs.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/reel/DcdL5uwTPTs/",
    description: "Vibrant botanical prints on featherlight cotton. Pair with shorts or chinos for an effortless look.",
    sizes: ["M", "L", "XL"]
  },
  {
    id: "HM-DNM-01",
    name: "Branded Comfort Stretch Denim Jeans",
    marathi: "ब्रँडेड कम्फर्ट स्ट्रेच डेनिम",
    category: "mens",
    subtype: "denim",
    price: 999,
    originalPrice: 1699,
    discount: "41% OFF",
    badge: "Showroom Hit",
    image: "assets/images/real_store_jeans.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/",
    description: "Heavy ring-spun cotton denim with 2% elastane for maximum movement. Available in light wash, mid-blue, and black.",
    sizes: ["28", "30", "32", "34", "36", "38", "40"]
  },
  {
    id: "HM-DNM-02",
    name: "Tailored Smart Fit Chinos & Trousers",
    marathi: "स्मार्ट फिट कॉटन ट्राउझर्स",
    category: "mens",
    subtype: "denim",
    price: 899,
    originalPrice: 1499,
    discount: "40% OFF",
    badge: "Daily Wear",
    image: "assets/images/real_store_center.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/",
    description: "Wrinkle-free combed cotton stretch chinos with clean pocket detailing. Colors: Khaki, Navy, Charcoal, Olive.",
    sizes: ["30", "32", "34", "36", "38"]
  },
  {
    id: "HM-ETH-01",
    name: "Royal Heritage Festive Kurta & Bundi Jacket",
    marathi: "हेरिटेज फेस्टिव्ह कुर्ता व जॅकेट",
    category: "mens",
    subtype: "ethnic",
    price: 1899,
    originalPrice: 2999,
    discount: "37% OFF",
    badge: "Celebration",
    image: "assets/images/hiramoti_interior_reception.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/",
    description: "Handcrafted festive ensemble featuring raw silk texture and subtle antique gold button accents for Satara weddings.",
    sizes: ["38", "40", "42", "44"]
  },
  {
    id: "HM-ETH-02",
    name: "Silk Blend Indo-Western Modi Jacket",
    marathi: "सिल्क ब्लेन्ड मोदी जॅकेट",
    category: "mens",
    subtype: "ethnic",
    price: 1299,
    originalPrice: 1999,
    discount: "35% OFF",
    badge: "Wedding Edit",
    image: "assets/images/hiramoti_interior_reception.jpg",
    reelUrl: "https://www.instagram.com/hiramoticollection/",
    description: "Rich jacquard textured sleeveless Nehru jacket. Pairs effortlessly over plain linen or cotton kurtas.",
    sizes: ["M", "L", "XL", "XXL"]
  }
];
