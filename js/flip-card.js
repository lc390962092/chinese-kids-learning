/**
 * 小豆中文公共JS模块
 * 抽取所有翻卡页共享的公共逻辑：
 * - 儿童锁（KidLock）
 * - 滑动手势翻页（SwipeNavigation）
 * - 音频控制（AudioController：stop / play / speakWithFallback）
 * - 应用启动（startApp：解锁AudioContext + 播放欢迎语）
 * - 公共 UI（showMascot / showStars / updateNavButtons / next / prev）
 */

(function () {
    'use strict';

    /* =====================================================
     * 通用工具
     * ===================================================== */
    function $(selector) { return document.querySelector(selector); }
    function $$(selector) { return document.querySelectorAll(selector); }

    /* =====================================================
     * 1. AudioController —— 全局音频管理
     * ===================================================== */
    let currentAudio = null;

    function stopAllAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio.onended = null;
            currentAudio.onerror = null;
            currentAudio = null;
        }
        document.querySelectorAll('audio').forEach(a => { a.pause(); a.currentTime = 0; });
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    }

    function playAudio(path) {
        stopAllAudio();
        return new Promise((resolve, reject) => {
            const audio = new Audio(XiaoDou.resolvePath(path));
            currentAudio = audio;
            audio.onended = () => { currentAudio = null; resolve(); };
            audio.onerror = (e) => { currentAudio = null; reject(e); };
            audio.play().catch(err => { currentAudio = null; reject(err); });
        });
    }

    /**
     * 优先播 MP3，失败回退 Web Speech API
     * @param {string}   text    回退朗读文本
     * @param {string}   mp3Path 本地音频路径（可空）
     * @param {string}   lang    'zh-CN' | 'ja-JP' | 'en-US'
     * @param {number}   rate    语速
     */
    function speakWithFallback(text, mp3Path, lang = 'zh-CN', rate = 0.8) {
        stopAllAudio();
        const langKey = lang.startsWith('ja') ? 'ja' : (lang.startsWith('en') ? 'en' : 'zh');
        if (mp3Path) {
            playAudio(mp3Path).catch(() => {
                console.log('MP3 播放失败，fallback 到 Web Speech API');
                XiaoDou.speak(text, langKey, rate);
            });
        } else {
            XiaoDou.speak(text, langKey, rate);
        }
    }

    /* =====================================================
     * 2. KidLock —— 儿童锁
     * ===================================================== */
    let kidLockOn = false;
    let kidLockKey = 'kidlock';   // 每页可覆盖
    let kidLockCallbacks = [];    // 锁定时执行的额外清理

    /**
     * @param {boolean} on
     */
    function toggleKidLock(on) {
        kidLockOn = !!on;
        try { localStorage.setItem(kidLockKey, kidLockOn ? '1' : '0'); } catch (e) {}
        document.body.classList.toggle('kidlock', kidLockOn);
        // 锁定时收起所有百科卡片，避免内容超出屏幕又滑不回去
        if (kidLockOn) {
            $$('.encyclopedia-card').forEach(el => el.style.display = 'none');
            kidLockCallbacks.forEach(fn => { try { fn(); } catch (e) {} });
        }
        showMascot(kidLockOn
            ? '儿童锁开启！页面锁住了，用两边的大箭头翻页～'
            : '儿童锁关闭。');
    }

    function initKidLock() {
        let saved = null;
        try { saved = localStorage.getItem(kidLockKey); } catch (e) {}
        const on = saved === '1';
        const toggle = $('#kidlockToggle');
        if (toggle) toggle.checked = on;
        document.body.classList.toggle('kidlock', on);
        kidLockOn = on;
    }

    function isKidLockOn() { return kidLockOn; }

    /** 注册锁定时的额外清理回调 */
    function onKidLock(fn) { kidLockCallbacks.push(fn); }

    /* =====================================================
     * 3. SwipeNavigation —— 滑动手势翻页
     * ===================================================== */
    let touchStartX = 0, touchStartY = 0, touchEndX = 0, touchEndY = 0;
    let touchTargetIsInteractive = false;
    let swipeThreshold = 60;  // 比原来小：轻轻滑也能翻页
    let swipeNextFn = null;
    let swipePrevFn = null;

    function isInteractiveTarget(el) {
        if (!el || !el.closest) return false;
        // 图片不算交互目标：解锁状态下支持"滑照片"翻页
        return !!el.closest('button, a, input, .btn, .side-arrow, .kidlock-bar');
    }

    /**
     * 初始化滑动手势
     * @param {Function} nextFn  下一页回调
     * @param {Function} prevFn  上一页回调
     * @param {Object}   opts    { threshold: number, stage: string }
     */
    function setupSwipe(nextFn, prevFn, opts = {}) {
        swipeNextFn = nextFn;
        swipePrevFn = prevFn;
        if (opts.threshold) swipeThreshold = opts.threshold;

        const stage = document.querySelector(opts.stage || '.main-stage');
        if (!stage) return;

        // 注意：不要在 touchstart 里 preventDefault！
        // 那会同时杀死 click 和垂直滚动。横向原生手势已由 CSS
        // touch-action: pan-y + body overscroll-behavior-x: none 禁用。

        stage.addEventListener('touchstart', function (e) {
            const t = e.changedTouches[0];
            touchStartX = t.screenX;
            touchStartY = t.screenY;
            touchTargetIsInteractive = isInteractiveTarget(e.target);
        }, { passive: true });

        stage.addEventListener('touchend', function (e) {
            const t = e.changedTouches[0];
            touchEndX = t.screenX;
            touchEndY = t.screenY;
            handleSwipe();
        }, { passive: true });

        let mouseDown = false;
        stage.addEventListener('mousedown', function (e) {
            mouseDown = true;
            touchStartX = e.screenX;
            touchStartY = e.screenY;
            touchTargetIsInteractive = isInteractiveTarget(e.target);
        });

        stage.addEventListener('mouseup', function (e) {
            if (!mouseDown) return;
            mouseDown = false;
            touchEndX = e.screenX;
            touchEndY = e.screenY;
            handleSwipe();
        });

        stage.addEventListener('mouseleave', function () { mouseDown = false; });
    }

    function handleSwipe() {
        if (kidLockOn) return; // 儿童锁：禁用滑动翻页

        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;
        const absX = Math.abs(diffX);
        const absY = Math.abs(diffY);

        // 1. 必须横向明显大于纵向（角度过滤）
        if (absY > absX) return;
        // 2. 水平距离达标
        if (absX < swipeThreshold) return;
        // 3. 起点不在按钮/链接/输入框上（图片可以）
        if (touchTargetIsInteractive) return;

        if (diffX > 0) { if (swipeNextFn) swipeNextFn(); }
        else           { if (swipePrevFn) swipePrevFn(); }
    }

    /* =====================================================
     * 4. 公共 UI
     * ===================================================== */
    function showMascot(text) {
        const el = $('#mascotText');
        if (el) el.textContent = text;
    }

    function showStars() {
        const star = $('#starEffect');
        if (!star) return;
        star.style.display = 'block';
        setTimeout(() => { star.style.display = 'none'; }, 1000);
    }

    /** 更新左右箭头禁用状态（通用版） */
    function updateNavButtons(cfg = {}) {
        const cards = cfg.cards || $$('.card');
        const current = cfg.current ?? 0;
        const total   = cfg.total ?? cards.length;
        $$(cfg.prevSelector || '.side-arrow.left').forEach(btn => btn.disabled = current === 0);
        $$(cfg.nextSelector || '.side-arrow.right').forEach(btn => btn.disabled = current === total - 1);
    }

    /* =====================================================
     * 5. App 启动
     * ===================================================== */
    let appStarted = false;

    /**
     * 解锁 AudioContext 并播放欢迎语
     * @param {string} welcomeText 欢迎语文本
     * @param {Object} opts { lang: 'zh', delay: 300 }
     */
    function startApp(welcomeText, opts = {}) {
        if (appStarted) return;
        appStarted = true;

        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            const ctx = new AudioContext();
            if (ctx.state === 'suspended') ctx.resume();
        }

        const silentAudio = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=');
        silentAudio.play().catch(() => {});

        if (welcomeText) {
            showMascot(welcomeText);
            const delay = opts.delay ?? 300;
            setTimeout(() => XiaoDou.speak(welcomeText, opts.lang || 'zh'), delay);
        }
    }

    /* =====================================================
     * 暴露到全局
     * ===================================================== */
    window.FlipCard = {
        // 音频
        stopAllAudio,
        playAudio,
        speakWithFallback,
        // 儿童锁
        toggleKidLock,
        initKidLock,
        isKidLockOn,
        onKidLock,
        set kidLockKey(v) { kidLockKey = v; },
        get kidLockKey()  { return kidLockKey; },
        // 滑动
        setupSwipe,
        // UI
        showMascot,
        showStars,
        updateNavButtons,
        // 启动
        startApp,
    };

})();
