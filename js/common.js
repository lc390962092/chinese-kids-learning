/**
 * 小豆中文通用模块加载器
 * 支持：GitHub Pages 子路径部署、JSON 数据加载、语音播放、卡片渲染
 */

(function() {
    'use strict';

    // 计算 basePath，支持 GitHub Pages 子路径部署
    const basePath = (typeof window !== 'undefined')
        ? window.location.pathname.replace(/\/[^/]*$/, '/')
        : '/';

    function resolvePath(relativePath) {
        if (relativePath.startsWith('http') || relativePath.startsWith('/')) return relativePath;
        // 去除开头的 ./
        const clean = relativePath.replace(/^\.\//, '');
        return basePath + clean;
    }

    // 全局语音状态
    let synth = null;
    let voicesLoaded = false;
    let voiceCache = { zh: null, ja: null, en: null };

    function initSpeech() {
        if (typeof window === 'undefined' || !window.speechSynthesis) return;
        synth = window.speechSynthesis;
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = refreshVoices;
        }
        refreshVoices();
    }

    function refreshVoices() {
        if (!synth) return;
        const voices = synth.getVoices() || [];
        voiceCache.zh = voices.find(v => v.lang === 'zh-CN') || voices.find(v => v.lang.startsWith('zh')) || null;
        voiceCache.ja = voices.find(v => v.lang === 'ja-JP') || voices.find(v => v.lang.startsWith('ja')) || null;
        voiceCache.en = voices.find(v => v.lang === 'en-US') || voices.find(v => v.lang.startsWith('en')) || null;
        voicesLoaded = true;
    }

    function speak(text, lang, rate = 0.85, pitch = 1.1) {
        if (!synth || !text) return false;
        synth.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = lang === 'ja' ? 'ja-JP' : (lang === 'en' ? 'en-US' : 'zh-CN');
        utter.rate = rate;
        utter.pitch = pitch;
        const voice = voiceCache[lang] || voiceCache.zh;
        if (voice) utter.voice = voice;
        synth.speak(utter);
        return true;
    }

    // 播放本地音频，失败则回退 TTS
    async function playAudio(path, fallbackText, lang) {
        const src = resolvePath(path);
        try {
            const audio = new Audio(src);
            await audio.play();
            return true;
        } catch (err) {
            console.log('本地音频播放失败:', src, err);
            if (fallbackText) speak(fallbackText, lang);
            return false;
        }
    }

    // 通用模块加载
    async function loadModule(moduleName) {
        const path = resolvePath(`content/${moduleName}_module.json`);
        try {
            const response = await fetch(path);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${path}`);
            const data = await response.json();
            return data;
        } catch (err) {
            console.error(`加载模块 ${moduleName} 失败:`, err);
            throw err;
        }
    }

    // 预加载图片（可选优化）
    function preloadImage(src) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = resolvePath(src);
        });
    }

    // 统一模块数据访问：words/items/sections/tales 都转成数组
    function getItems(data) {
        if (!data) return [];
        for (const key of ['words', 'items', 'tales']) {
            if (Array.isArray(data[key])) return data[key];
        }
        if (Array.isArray(data.sections)) {
            // 拼音等分节模块，把所有 items 拍平
            return data.sections.flatMap(s => s.items || []);
        }
        return [];
    }

    // 安全 HTML 转义
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // 暴露到全局
    window.XiaoDou = {
        basePath,
        resolvePath,
        loadModule,
        initSpeech,
        speak,
        playAudio,
        preloadImage,
        getItems,
        escapeHtml,
        get voices() { return voiceCache; }
    };

    // 自动初始化语音
    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initSpeech);
        } else {
            initSpeech();
        }
    }
})();
