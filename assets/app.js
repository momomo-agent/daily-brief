// 加载日期索引
async function loadIndex() {
  const res = await fetch('data/index.json');
  return res.json();
}

// 加载单日数据
async function loadDay(date) {
  const res = await fetch(`data/${date}.json`);
  return res.json();
}

// 渲染单张报纸
function renderPaper(data) {
  const paper = document.createElement('article');
  paper.className = 'newspaper';
  paper.id = `paper-${data.date}`;
  
  let sectionsHtml = '';
  data.sections.forEach(section => {
    sectionsHtml += `<h2 class="section-title">${section.title}</h2>`;
    section.items.forEach(item => {
      sectionsHtml += renderItem(item);
    });
  });
  
  paper.innerHTML = `
    <header class="paper-header">
      <div class="paper-date">${formatDate(data.date)}</div>
      <h1 class="paper-title">${data.title}</h1>
      <div class="paper-tagline">AI · OS · Graphics</div>
    </header>
    <div class="paper-content">
      ${sectionsHtml}
    </div>
  `;
  
  return paper;
}

function renderItem(item) {
  return `
    <div class="news-item">
      <h3 class="news-title">
        <a href="${item.url}" target="_blank">${item.title}</a>
      </h3>
      <p class="news-desc">${item.desc}</p>
      <span class="news-source">${item.source}</span>
      ${item.momo ? `<p class="news-momo">✨ ${item.momo}</p>` : ''}
    </div>
  `;
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December'];
  return `${days[d.getDay()]}, ${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

function renderDateNav(dates) {
  const nav = document.getElementById('dateNav');
  dates.forEach((date, i) => {
    const dot = document.createElement('div');
    dot.className = 'date-dot' + (i === 0 ? ' active' : '');
    dot.title = date;
    dot.onclick = () => {
      document.getElementById(`paper-${date}`)?.scrollIntoView({ behavior: 'smooth' });
      document.querySelectorAll('.date-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
    };
    nav.appendChild(dot);
  });
}

async function init() {
  const index = await loadIndex();
  const container = document.getElementById('papers');
  
  renderDateNav(index.dates);
  
  for (const date of index.dates) {
    const data = await loadDay(date);
    container.appendChild(renderPaper(data));
  }
}

init();
