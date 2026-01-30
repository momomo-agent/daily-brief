const recent = [
  {
    date: '2026-01-30',
    title: '今日简报 · AI / OS / 图形学',
    desc: 'Hacker News / The Verge / Reddit 等来源速览，附链接与短评。',
    href: 'daily/2026-01-30.html'
  }
];

const grid = document.getElementById('recent-grid');
if (grid) {
  grid.innerHTML = recent.map(item => `
    <div class="card">
      <div class="title">${item.title}</div>
      <div class="meta">${item.date}</div>
      <div class="desc">${item.desc}</div>
      <a href="${item.href}">打开详情 →</a>
    </div>
  `).join('');
}
