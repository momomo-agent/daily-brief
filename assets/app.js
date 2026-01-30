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
      <span class="chip">${item.subtitle || '简报'}</span>
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

async function loadDaily(date) {
  const res = await fetch(`./data/${date}.json`);
  const data = await res.json();
  document.getElementById('daily-title').textContent = `${date} · ${data.title}`;

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
            <a href="${it.url}" target="_blank">直达原文 →</a>
          </div>
        `).join('')}
      </div>
    </section>
  `).join('');

  renderNav(date);
}

(async () => {
  await fetchIndex();
  const firstDate = indexData.items[0].date;
  await loadDaily(firstDate);
})();
