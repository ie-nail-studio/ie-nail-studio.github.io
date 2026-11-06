// i.e. NAIL STUDIO — MPA 共用互動腳本

document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initStartMenu();
    initClock();
    initBookingForm();
    initGalleryTabs();
});

function initMobileNav() {
    const menuToggle = document.getElementById('menu-toggle');
    const menuClose = document.getElementById('menu-close');
    const navLinks = document.getElementById('nav-links');

    if (menuToggle && navLinks) {
        // 1. 改用 toggle：點擊漢堡圖示可以「開啟 / 關閉」切換
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation(); // 防止點擊事件冒泡觸發全域點擊關閉
            navLinks.classList.toggle('show');
        });
    }

    if (menuClose && navLinks) {
        // 2. 點擊 X 按鈕：關閉選單
        menuClose.addEventListener('click', (e) => {
            e.stopPropagation();
            navLinks.classList.remove('show');
        });
    }

    // 3. 點擊導覽連結後自動收合選單
    navLinks?.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('show');
        });
    });

    // 4. 新增：點擊選單以外的空白區域，自動收合選單
    document.addEventListener('click', (e) => {
        if (navLinks && navLinks.classList.contains('show')) {
            // 如果點擊的地方既不是選單內部，也不是漢堡按鈕，就收起選單
            if (!navLinks.contains(e.target) && !menuToggle?.contains(e.target)) {
                navLinks.classList.remove('show');
            }
        }
    });
}

// 關閉公告 Banner
function closeBanner() {
    const promoBanner = document.getElementById('promo-banner');
    if (promoBanner) {
        promoBanner.style.display = 'none';
    }
}

// 開始功能表
function toggleStartMenu() {
    const startMenu = document.getElementById('start-menu');
    if (startMenu) {
        startMenu.classList.toggle('show');
    }
}

function initStartMenu() {
    document.addEventListener('click', (e) => {
        const startMenu = document.getElementById('start-menu');
        const startBtn = document.querySelector('.win95-start-btn');
        if (startMenu?.classList.contains('show')) {
            if (!startMenu.contains(e.target) && !startBtn?.contains(e.target)) {
                startMenu.classList.remove('show');
            }
        }
    });
}

// 系統時鐘
function initClock() {
    const clockText = document.getElementById('clock-text');
    if (!clockText) return;

    function updateClock() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        clockText.textContent = `${hours}:${minutes} ${ampm}`;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

// 預約表單嵌入（僅 booking.html）
function initBookingForm() {
    const wrapper = document.getElementById('form-embed-wrapper');
    if (!wrapper) return;

    window.openEmbeddedForm = function(type) {
        const container = document.getElementById('embed-container');
        const formTitle = document.getElementById('form-title');

        if (!container || !formTitle) return;

        wrapper.style.display = 'block';

        if (type === 'new') {
            formTitle.textContent = 'NEW_CLIENT_BOOKING_FORM.exe';
            container.innerHTML = `
                <div class="embed-placeholder">
                    <i class="fa-solid fa-file-signature" style="font-size: 32px; margin-bottom: 10px; color: #000080;"></i>
                    <p style="font-weight: bold; margin-bottom: 5px;">[新客預約表單載入中]</p>
                    <p style="font-size: 12px; color: #555;">正在準備您的首次美甲諮詢與健康評估...</p>
                    <iframe src="about:blank" style="width:100%; height:350px; border:2px inset #fff; margin-top:15px; background:#fff;" title="New Client Form"></iframe>
                </div>
            `;
        } else {
            formTitle.textContent = 'RETURNING_CLIENT_BOOKING_FORM.exe';
            container.innerHTML = `
                <div class="embed-placeholder">
                    <i class="fa-solid fa-heart" style="font-size: 32px; margin-bottom: 10px; color: #ff0055;"></i>
                    <p style="font-weight: bold; margin-bottom: 5px;">[舊客快速預約載入中]</p>
                    <p style="font-size: 12px; color: #555;">老朋友好！正在載入您的快速預約通道...</p>
                    <iframe src="about:blank" style="width:100%; height:350px; border:2px inset #fff; margin-top:15px; background:#fff;" title="Returning Client Form"></iframe>
                </div>
            `;
        }

        wrapper.scrollIntoView({ behavior: 'smooth' });
    };

    window.closeEmbedForm = function() {
        wrapper.style.display = 'none';
    };
}


function closePopup() {
    document.getElementById('promo-popup').style.display = 'none';
}



document.addEventListener('DOMContentLoaded', function () {
    const popup = document.getElementById('promo-popup');
    const lastClosedDate = localStorage.getItem('promo_popup_closed_date');
    const today = new Date().toDateString(); // 取得今天的日期字串 (例: "Sun Aug 09 2026")

    // 如果今天已經關閉過，就直接隱藏視窗
    if (lastClosedDate === today) {
        if (popup) popup.style.display = 'none';
    } else {
        if (popup) popup.style.display = 'flex';
    }
});

// 點擊「我知道了」或「X」關閉視窗並記錄今日日期
function closePopupWithStorage() {
    const popup = document.getElementById('promo-popup');
    const today = new Date().toDateString();
    
    // 將今天日期存進瀏覽器的 localStorage
    localStorage.setItem('promo_popup_closed_date', today);
    
    if (popup) {
        popup.style.display = 'none';
    }
}

// 輪播圖

function initCarousel() {
const slide = document.getElementById('carouselSlide');
const images = document.querySelectorAll('.carousel-slide img');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
// 🔑 1. 補上計數器元素的宣告
const counterText = document.getElementById('carouselCounter'); 

let counter = 0;
const totalSlides = images.length;
if (!slide || !prevBtn || !nextBtn || !totalSlides) return;

// 🔑 2. 建立統一更新畫面與頁碼的函式
function updateCarousel() {
  slide.style.transform = `translateX(${-counter * 100}%)`;
  
  // 更新頁碼文字 [ 當前頁數 / 總頁數 ]
  if (counterText) {
    counterText.textContent = `[ ${counter + 1} / ${totalSlides} ]`;
  }
}

// 下一張
function nextSlide() {
  if (counter >= totalSlides - 1) {
    counter = 0; // 最後一張時重置回第一張
  } else {
    counter++;
  }
  updateCarousel(); // 🔑 3. 呼叫更新
}

// 上一張
function prevSlide() {
  if (counter <= 0) {
    counter = totalSlides - 1; // 第一張時跳到最後一張
  } else {
    counter--;
  }
  updateCarousel(); // 🔑 3. 呼叫更新
}

// 綁定按鈕事件
nextBtn.addEventListener('click', nextSlide);
prevBtn.addEventListener('click', prevSlide);

// 自動輪播 (每 5 秒切換一次)
setInterval(nextSlide, 5000);

}
initCarousel();

// 作品分類列只水平捲動，避免移動整個頁面。
function initGalleryTabs() {
    document.querySelectorAll('.gallery-tabs').forEach(tabs => {
        const active = tabs.querySelector('[aria-current="page"]');
        const hint = tabs.nextElementSibling;
        const update = () => {
            if (hint?.classList.contains('gallery-tabs-hint')) {
                hint.hidden = tabs.scrollWidth <= tabs.clientWidth + 1;
            }
            if (active) {
                const tabRect = active.getBoundingClientRect();
                const listRect = tabs.getBoundingClientRect();
                if (tabRect.left < listRect.left || tabRect.right > listRect.right) {
                    tabs.scrollLeft += tabRect.left - listRect.left - (tabs.clientWidth - active.offsetWidth) / 2;
                }
            }
        };
        update();
        window.addEventListener('resize', update);
        if (document.fonts) document.fonts.ready.then(update);
    });
}
