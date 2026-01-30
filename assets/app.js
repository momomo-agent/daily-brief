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
      const date = a.getAttribute('data-date');
      loadDaily(date);
    });
  });
}

function coverClass(sectionTitle){
  const t = sectionTitle.toLowerCase();
  if (t.includes('ai')) return 'cover ai';
  if (t.includes('os') || t.includes('系统')) return 'cover os';
  if (t.includes('图形')) return 'cover graphics';
  if (t.includes('社区')) return 'cover community';
  return 'cover';
}

async function loadDaily(date) {
  const res = await fetch(`./data/${date}.json`);
  const data = await res.json();
  document.getElementById('daily-title').textContent = `${date} · ${data.title}`;

  const container = document.getElementById('daily-sections');
  container.innerHTML = `<div class="masonry">` + data.sections.map(sec => `
    ${sec.items.map(it => `
      <div class="card">
        <div class="${coverClass(sec.title)}"></div>
        <div class="title">${it.title}</div>
        <div class="meta">${sec.title} · ${it.source || '来源'}</div>
        <div class="desc">${it.desc}</div>
        <a href="${it.url}" target="_blank">打开原文 →</a>
      </div>
    `).join('')}
  `).join('') + `</div>`;

  renderNav(date);
}

(async () => {
  await fetchIndex();
  const firstDate = indexData.items[0].date;
  await loadDaily(firstDate);
})();
