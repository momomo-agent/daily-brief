let indexData = null;

async function fetchIndex() {
  const res = await fetch('./data/index.json');
  indexData = await res.json();
}

function renderNav(selectedDate) {
  const nav = document.getElementById('date-nav');
  if (!nav || !indexData) return;
  nav.innerHTML = indexData.items.map(item => `
    <a class="date-link ${item.date===selectedDate?'active':''}" href="#" data-date="${item.date}">
      <span>${item.date}</span>
      <span>${item.subtitle || '简报'}</span>
    </a>
  `).join('');
  nav.querySelectorAll('.date-link').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      loadDaily(a.getAttribute('data-date'));
    });
  });
}

function coverClass(sectionTitle) {
  const t = sectionTitle.toLowerCase();
  if (t.includes('ai') || t.includes('模型')) return 'card-cover ai';
  if (t.includes('os') || t.includes('系统')) return 'card-cover os';
  if (t.includes('图形') || t.includes('交互')) return 'card-cover graphics';
  if (t.includes('社区')) return 'card-cover community';
  return 'card-cover';
}

function coverIcon(sectionTitle) {
  const t = sectionTitle.toLowerCase();
  if (t.includes('ai') || t.includes('模型')) return '🤖';
  if (t.includes('os') || t.includes('系统')) return '💻';
  if (t.includes('图形') || t.includes('交互')) return '🎨';
  if (t.includes('社区')) return '💬';
  return '📰';
}

async function loadDaily(date) {
  const res = await fetch(`./data/${date}.json`);
  const data = await res.json();
  document.getElementById('daily-title').textContent = `${date} · ${data.title}`;

  const container = document.getElementById('daily-sections');
  let html = '<div class="masonry">';
  data.sections.forEach(sec => {
    sec.items.forEach(it => {
      html += `
        <div class="card">
          <div class="${coverClass(sec.title)}">${coverIcon(sec.title)}</div>
          <div class="card-body">
            <div class="title">${it.title}</div>
            <div class="meta">${sec.title} · ${it.source || '来源'}</div>
            <div class="desc">${it.desc}</div>
            ${it.momo ? `<div class="momo-take">${it.momo}</div>` : ''}
            <a href="${it.url}" target="_blank">打开原文 →</a>
          </div>
        </div>`;
    });
  });
  html += '</div>';
  container.innerHTML = html;
  renderNav(date);
}

(async () => {
  await fetchIndex();
  const firstDate = indexData.items[0].date;
  await loadDaily(firstDate);
})();
