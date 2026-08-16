/**
 * 小侦探模块
 * 负责：首页、案件页、观察训练营的渲染和交互
 */

const Detective = (function() {
  'use strict';

  const STORAGE_KEY = 'detective_progress';
  const DEFAULT_BADGE = 'assets/images/detective/badges/badge-locked.png';

  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveProgress(progress) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function hasBadge(caseId) {
    const p = getProgress();
    return (p.badges || []).includes(caseId);
  }

  function awardBadge(caseId) {
    const p = getProgress();
    p.badges = p.badges || [];
    if (!p.badges.includes(caseId)) {
      p.badges.push(caseId);
      saveProgress(p);
    }
  }

  function showError(container, message) {
    container.innerHTML = `
      <div class="error-card">
        <p>🤔 ${XiaoDou.escapeHtml(message)}</p>
        <a class="btn-primary" href="detective.html">返回侦探事务所</a>
      </div>
    `;
  }

  async function loadCasesData() {
    const data = await XiaoDou.loadModule('detective_cases');
    return data;
  }

  async function loadObserveData() {
    const data = await XiaoDou.loadModule('detective_observe');
    return data;
  }

  // ================= 首页 =================
  function renderHome() {
    const main = document.getElementById('main');
    if (!main) return;

    loadCasesData().then(data => {
      const progress = getProgress();
      const badges = progress.badges || [];
      const badgeContainer = document.getElementById('badges');

      if (badgeContainer) {
        if (badges.length === 0) {
          badgeContainer.innerHTML = '<p class="empty">还没有徽章，快去破案吧！</p>';
        } else {
          badgeContainer.innerHTML = data.cases.map(c => {
            const unlocked = badges.includes(c.id);
            return `
              <div class="badge-item ${unlocked ? '' : 'locked'}">
                <img src="${XiaoDou.resolvePath(unlocked ? (c.badge || DEFAULT_BADGE) : DEFAULT_BADGE)}"
                     alt="${XiaoDou.escapeHtml(c.title)}" onerror="this.src='${XiaoDou.resolvePath(DEFAULT_BADGE)}'">
                <span>${XiaoDou.escapeHtml(c.title)}</span>
              </div>
            `;
          }).join('');
        }
      }
    }).catch(err => {
      console.error('加载首页失败:', err);
    });
  }

  // ================= 案件页 =================
  async function loadCase(id) {
    const main = document.getElementById('main');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');

    try {
      const data = await loadCasesData();
      const c = data.cases.find(x => x.id === id);
      if (!c) throw new Error(`找不到案件：${id}`);

      if (loading) loading.style.display = 'none';
      if (error) error.style.display = 'none';
      renderCase(main, c);
    } catch (err) {
      if (loading) loading.style.display = 'none';
      showError(main, err.message || '案件加载失败，请检查网络或文件路径。');
    }
  }

  function renderCase(container, c) {
    const titleEl = document.getElementById('page-title');
    if (titleEl) titleEl.textContent = c.title;

    const alreadySolved = hasBadge(c.id);

    container.innerHTML = `
      <section class="case-intro card">
        <h2>📜 案情</h2>
        <p>${XiaoDou.escapeHtml(c.intro)}</p>
        <p class="scene-text">${XiaoDou.escapeHtml(c.scene)}</p>
        <button class="btn-speak" onclick="Detective.speakText('${XiaoDou.escapeHtml(c.intro + c.scene)}')">🔊 读给我听</button>
      </section>

      <section class="case-scene card">
        <h2>🔍 现场</h2>
        <div class="scene-image">
          <img src="${XiaoDou.resolvePath(c.sceneImage || '')}" alt="案件现场" onerror="this.style.display='none'">
          <p class="scene-hint">（图片加载失败时，请根据文字线索推理）</p>
        </div>
      </section>

      <section class="case-clues card">
        <h2>🧩 线索</h2>
        <ul>
          ${c.clues.map(cl => `<li>${XiaoDou.escapeHtml(cl)}</li>`).join('')}
        </ul>
      </section>

      <section class="case-suspects card">
        <h2>🧑 嫌疑人</h2>
        <p class="hint">💡 提示：${XiaoDou.escapeHtml(c.hint)}</p>
        <div class="suspect-list">
          ${c.suspects.map((s, i) => `
            <button class="suspect-btn" onclick="Detective.guess('${c.id}', ${i})">
              <img class="avatar" src="${XiaoDou.resolvePath(s.avatar || '')}" alt="${XiaoDou.escapeHtml(s.name)}" onerror="this.outerHTML='<span class=\'avatar-fallback\'>${s.emoji || '❓'}</span>'">
              <div class="suspect-info">
                <strong>${XiaoDou.escapeHtml(s.name)}</strong>
                <p>${XiaoDou.escapeHtml(s.statement)}</p>
              </div>
            </button>
          `).join('')}
        </div>
      </section>

      <div id="case-result" class="result"></div>

      ${alreadySolved ? '<div class="solved-banner">🏆 这个案件你已经破解过了！</div>' : ''}
    `;
  }

  async function guess(caseId, suspectIndex) {
    const data = await loadCasesData();
    const c = data.cases.find(x => x.id === caseId);
    if (!c) return;

    const suspect = c.suspects[suspectIndex];
    const resultEl = document.getElementById('case-result');

    if (suspect.name === c.answer) {
      awardBadge(caseId);
      resultEl.innerHTML = `
        <div class="success-card">
          <h3>🎉 破案成功！</h3>
          <p>${XiaoDou.escapeHtml(c.solution)}</p>
          <img class="badge-img" src="${XiaoDou.resolvePath(c.badge || DEFAULT_BADGE)}" alt="徽章" onerror="this.style.display='none'">
          <div>
            <a class="btn-primary" href="detective.html">返回事务所</a>
            <a class="btn-secondary" href="detective_observe.html">去训练观察力</a>
          </div>
        </div>
      `;
      XiaoDou.speak('答对了！' + c.solution);
    } else {
      resultEl.innerHTML = `
        <div class="wrong-card">
          <h3>❌ 还不是正确答案</h3>
          <p>${XiaoDou.escapeHtml(suspect.contradiction)}</p>
          <button class="btn-secondary" onclick="Detective.speakText('${XiaoDou.escapeHtml(suspect.contradiction)}')">🔊 再听一遍</button>
        </div>
      `;
      XiaoDou.speak('不对哦。' + suspect.contradiction);
    }
  }

  function speakText(text) {
    XiaoDou.speak(text);
  }

  // ================= 观察训练营 =================
  async function loadObserve() {
    const main = document.getElementById('main');
    const loading = document.getElementById('loading');

    try {
      const data = await loadObserveData();
      if (loading) loading.style.display = 'none';
      renderObserve(main, data, 0);
    } catch (err) {
      if (loading) loading.style.display = 'none';
      showError(main, err.message || '观察场景加载失败。');
    }
  }

  function renderObserve(container, data, levelIndex) {
    const level = data.levels[levelIndex];
    if (!level) {
      container.innerHTML = `
        <div class="success-card">
          <h3>🎉 观察训练营全部完成！</h3>
          <p>你已经是小小观察家了，快去破解真正的案件吧。</p>
          <a class="btn-primary" href="detective.html">返回侦探事务所</a>
        </div>
      `;
      return;
    }

    const totalIntruders = level.items.filter(i => i.isIntruder).length;
    let found = 0;

    container.innerHTML = `
      <section class="observe-card card">
        <h2>${XiaoDou.escapeHtml(level.title)}</h2>
        <p>${XiaoDou.escapeHtml(level.description)}</p>
        <p class="hint">💡 ${XiaoDou.escapeHtml(level.hint)}</p>
        <div class="progress-bar">
          <span id="observe-progress">找到 0 / ${totalIntruders} 个</span>
        </div>
        <div class="scene-container" id="scene-container">
          <img class="scene-bg" src="${XiaoDou.resolvePath(level.background || '')}" alt="观察场景" onerror="this.style.display='none'">
          ${level.items.map((item, i) => `
            <button class="scene-item" style="left:${item.x}%; top:${item.y}%;" data-index="${i}" aria-label="${XiaoDou.escapeHtml(item.name)}"></button>
          `).join('')}
        </div>
        <div id="observe-result"></div>
      </section>
    `;

    const buttons = container.querySelectorAll('.scene-item');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.index, 10);
        const item = level.items[idx];
        if (btn.classList.contains('checked')) return;
        btn.classList.add('checked');

        const resultEl = document.getElementById('observe-result');
        if (item.isIntruder) {
          found++;
          btn.classList.add('found');
          document.getElementById('observe-progress').textContent = `找到 ${found} / ${totalIntruders} 个`;
          XiaoDou.speak(`找到了${item.name}！`);

          if (found >= totalIntruders) {
            resultEl.innerHTML = `
              <div class="success-card">
                <h3>🎉 全部找到！</h3>
                <p>观察力 +1，继续下一关吧！</p>
                <button class="btn-primary" onclick="Detective.nextObserveLevel(${levelIndex + 1})">下一关</button>
              </div>
            `;
            XiaoDou.speak('太棒了，全部找到了！');
          }
        } else {
          btn.classList.add('wrong');
          resultEl.innerHTML = `
            <div class="wrong-card">
              <p>${XiaoDou.escapeHtml(item.name)} 确实在这里，不是要找的东西。</p>
            </div>
          `;
          XiaoDou.speak(`${item.name} 不是要找的哦。`);
        }
      });
    });
  }

  async function nextObserveLevel(index) {
    const main = document.getElementById('main');
    const data = await loadObserveData();
    renderObserve(main, data, index);
  }

  // 暴露公共 API
  return {
    renderHome,
    loadCase,
    guess,
    speakText,
    loadObserve,
    nextObserveLevel
  };
})();
