async function loadIndex() {
  const res = await fetch('./data/index.json');
  const data = await res.json();
  const grid = document.getElementById('recent-grid');
  if (!grid) return;
  grid.innerHTML = data.items.map(item => `
    <div class="card">
      <div class="title">${item.title}</div>
      <div class="meta"><span class="chip">${item.date}</span><span>${item.subtitle || ''}</span></div>
      <div class="desc">${item.desc}</div>
      <div class="link-row"><a href="daily/${item.date}.html">打开详情 →</a></div>
    </div>
  `).join('');
}

async function loadDaily() {
  const root = document.getElementById('daily-root');
  if (!root) return;
  const date = root.dataset.date;
  const res = await fetch(`../data/${date}.json`);
  const data = await res.json();

  document.getElementById('daily-title').textContent = data.title;

  const sections = document.getElementById('daily-sections');
  sections.innerHTML = data.sections.map(sec => `
    <section class="board">
      <h2>${sec.title}</h2>
      <div class="grid">
        ${sec.items.map(it => `
          <div class="card">
            <div class="title">${it.title}</div>
            <div class="meta"><span class="chip">${it.source || '来源'}</span></div>
            <div class="desc">${it.desc}</div>
            <div class="link-row"><a href="${it.url}" target="_blank">直达原文 →</a></div>
          </div>
        `).join('')}
      </div>
    </section>
  `).join('');
}

loadIndex();
loadDaily();
