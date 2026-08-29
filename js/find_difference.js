/**
 * 图片找不同模块
 * 左右两幅图，点击右图找出差异
 */
const FindDifference = (function() {
  'use strict';

  const STORAGE_KEY = 'find_difference_progress';
  let levels = [];
  let currentIndex = 0;
  let foundIds = new Set();

  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { completed: [], best: {} };
    } catch (e) {
      return { completed: [], best: {} };
    }
  }

  function saveProgress(progress) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function markCompleted(levelId) {
    const p = getProgress();
    if (!p.completed.includes(levelId)) {
      p.completed.push(levelId);
      saveProgress(p);
    }
  }

  async function init() {
    try {
      const data = await XiaoDou.loadModule('find_difference');
      levels = (data && data.levels) || [];
      if (!levels.length) throw new Error('没有关卡数据');
      document.getElementById('loading').style.display = 'none';
      document.getElementById('gameArea').style.display = 'block';
      renderLevelBar();
      loadLevel(0);
    } catch (err) {
      document.getElementById('loading').style.display = 'none';
      const errorEl = document.getElementById('error');
      errorEl.style.display = 'block';
      errorEl.textContent = '加载失败：' + (err.message || '请检查网络后刷新');
      console.error(err);
    }
  }

  function renderLevelBar() {
    const bar = document.getElementById('levelBar');
    bar.innerHTML = levels.map((level, i) => {
      const progress = getProgress();
      const completed = progress.completed.includes(level.id);
      return `<button class="level-btn ${i === currentIndex ? 'active' : ''}" data-index="${i}" onclick="FindDifference.selectLevel(${i})">${completed ? '🏅 ' : ''}第${i + 1}关</button>`;
    }).join('');
  }

  function selectLevel(index) {
    if (index === currentIndex) return;
    loadLevel(index);
  }

  function loadLevel(index) {
    currentIndex = index;
    foundIds.clear();
    renderLevelBar();
    const level = levels[index];
    document.getElementById('levelName').textContent = level.title || `第${index + 1}关`;
    document.body.style.background = level.bgColor || 'linear-gradient(135deg, #FFF3E0 0%, #E3F2FD 100%)';
    document.getElementById('mascotText').textContent = level.description || '仔细观察左右两幅图，找出不一样的地方吧！';
    document.getElementById('foundCount').textContent = '0';
    document.getElementById('totalCount').textContent = (level.differences || []).length;
    document.getElementById('resultArea').innerHTML = '';
    document.getElementById('nextBtn').style.display = 'none';
    document.getElementById('hintBtn').style.display = 'inline-block';
    renderScenes(level);
    speakTask();
  }

  function getItemForSide(item, overrides) {
    if (!overrides) return item;
    return Object.assign({}, item, overrides);
  }

  function renderScenes(level) {
    const left = document.getElementById('leftScene');
    const right = document.getElementById('rightScene');
    left.innerHTML = '';
    right.innerHTML = '';
    const overrides = level.rightOverrides || {};
    level.itemsPerSide.forEach((item, i) => {
      const leftEl = createItemElement(item, i, 'left');
      const rightItem = getItemForSide(item, overrides[i]);
      const rightEl = createItemElement(rightItem, i, 'right');
      left.appendChild(leftEl);
      right.appendChild(rightEl);
    });
  }

  function createItemElement(item, index, side) {
    const el = document.createElement('div');
    el.className = 'scene-item' + (item.hidden ? ' hidden' : '');
    el.dataset.index = index;
    el.dataset.side = side;
    el.style.left = (item.x || 0) + '%';
    el.style.top = (item.y || 0) + '%';
    el.style.width = (item.size || 60) + 'px';
    el.style.height = (item.size || 60) + 'px';

    if (item.image) {
      const img = document.createElement('img');
      img.src = XiaoDou.resolvePath(item.image);
      img.alt = item.name || '';
      img.onerror = function() {
        this.style.display = 'none';
        const emoji = document.createElement('span');
        emoji.className = 'emoji';
        emoji.textContent = item.emoji || '❓';
        el.appendChild(emoji);
      };
      el.appendChild(img);
    } else {
      const emoji = document.createElement('span');
      emoji.className = 'emoji';
      emoji.textContent = item.emoji || '❓';
      el.appendChild(emoji);
    }

    if (side === 'right') {
      el.addEventListener('click', () => handleRightClick(index, el));
      el.addEventListener('touchstart', (e) => e.preventDefault(), { passive: false });
    }
    return el;
  }

  function handleRightClick(index, el) {
    if (el.classList.contains('found')) return;
    if (foundIds.has(index)) return;

    const level = levels[currentIndex];
    const diff = (level.differences || []).find(d => d.index === index);
    if (diff) {
      foundIds.add(index);
      el.classList.add('found');
      document.getElementById('foundCount').textContent = foundIds.size;
      const msg = `找到了！${diff.name} ${diff.type === 'missing' ? '不见了' : (diff.type === 'moved' ? '位置变了' : '变了样')}`;
      XiaoDou.speak(msg);
      updateMascot(msg);
      checkComplete(level);
    } else {
      el.classList.add('wrong');
      XiaoDou.speak('这里不是哦，再看看别的地方');
      setTimeout(() => el.classList.remove('wrong'), 400);
    }
  }

  function checkComplete(level) {
    const total = (level.differences || []).length;
    if (foundIds.size >= total) {
      markCompleted(level.id);
      renderLevelBar();
      const result = document.getElementById('resultArea');
      result.innerHTML = `
        <div class="success-card">
          <h3>🎉 太棒了！</h3>
          <p>你找到了全部 ${total} 处不同，观察力超强！</p>
        </div>
      `;
      XiaoDou.speak(`太棒了！你找到了全部${total}处不同，观察力超强！`);
      updateMascot('全部找到啦！要不要挑战下一关？');
      document.getElementById('hintBtn').style.display = 'none';
      const nextBtn = document.getElementById('nextBtn');
      if (currentIndex < levels.length - 1) {
        nextBtn.textContent = '➡️ 下一关';
        nextBtn.style.display = 'inline-block';
      } else {
        nextBtn.textContent = '🏆 重新开始第一关';
        nextBtn.style.display = 'inline-block';
      }
    }
  }

  function showHint() {
    const level = levels[currentIndex];
    const remaining = (level.differences || []).filter(d => !foundIds.has(d.index));
    if (!remaining.length) return;
    // 给所有剩余差异项加提示光环，3 秒后移除
    remaining.forEach(d => {
      const el = document.querySelector(`.scene-item[data-side="right"][data-index="${d.index}"]`);
      if (el) el.classList.add('hint-ring');
    });
    XiaoDou.speak('注意这些闪闪发光的地方哦');
    setTimeout(() => {
      document.querySelectorAll('.scene-item.hint-ring').forEach(el => el.classList.remove('hint-ring'));
    }, 2500);
  }

  function nextLevel() {
    const next = (currentIndex + 1) % levels.length;
    loadLevel(next);
  }

  function speakTask() {
    const level = levels[currentIndex];
    const text = (level.title || '') + '。' + (level.description || '') + '。' + (level.hint || '');
    XiaoDou.speak(text);
  }

  function updateMascot(text) {
    document.getElementById('mascotText').textContent = text;
  }

  return {
    init,
    selectLevel,
    nextLevel,
    showHint,
    speakTask
  };
})();
