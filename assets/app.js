let papers = [];
let currentIndex = 0;
let startX = 0;
let isDragging = false;

async function loadIndex() {
  const res = await fetch('data/index.json');
  return res.json();
}

async function loadDay(date) {
  const res = await fetch(`data/${date}.json`);
  return res.json();
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${days[d.getDay()]}, ${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

function renderPaper(data, index) {
  const paper = document.createElement('article');
  paper.className = 'newspaper';
  paper.dataset.index = index;
  
  let sectionsHtml = '';
  data.sections.forEach(section => {
    sectionsHtml += `<h2 class="section-title">${section.title}</h2>`;
    section.items.forEach(item => {
      sectionsHtml += `
        <div class="news-item">
          <h3 class="news-title"><a href="${item.url}" target="_blank">${item.title}</a></h3>
          <p class="news-desc">${item.desc}</p>
          <span class="news-source">${item.source}</span>
          ${item.momo ? `<p class="news-momo">✨ ${item.momo}</p>` : ''}
        </div>`;
    });
  });
  
  paper.innerHTML = `
    <header class="paper-header">
      <div class="paper-date">${formatDate(data.date)}</div>
      <h1 class="paper-title">${data.title}</h1>
      <div class="paper-tagline">AI · Policy · Tech</div>
    </header>
    <div class="paper-content">${sectionsHtml}</div>
  `;
  return paper;
}

function updatePositions() {
  papers.forEach((paper, i) => {
    paper.classList.remove('active', 'prev', 'next', 'hidden');
    if (i === currentIndex) paper.classList.add('active');
    else if (i === currentIndex - 1) paper.classList.add('prev');
    else if (i === currentIndex + 1) paper.classList.add('next');
    else paper.classList.add('hidden');
  });
  updateDots();
  updateArrows();
}

function updateDots() {
  document.querySelectorAll('.nav-dot').forEach((dot, i) => {
    dot.classList.toggle('active', i === currentIndex);
  });
}

function updateArrows() {
  document.getElementById('prevBtn').classList.toggle('disabled', currentIndex === 0);
  document.getElementById('nextBtn').classList.toggle('disabled', currentIndex === papers.length - 1);
}

function goTo(index) {
  if (index < 0 || index >= papers.length) return;
  currentIndex = index;
  updatePositions();
}

function prev() { goTo(currentIndex - 1); }
function next() { goTo(currentIndex + 1); }

function handleStart(e) {
  isDragging = true;
  startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
}

function handleMove(e) {
  if (!isDragging) return;
  const x = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
  const diff = x - startX;
  const paper = papers[currentIndex];
  if (paper) {
    paper.style.transform = `translateX(-50%) translateX(${diff * 0.5}px) rotateY(${-diff * 0.02}deg)`;
  }
}

function handleEnd(e) {
  if (!isDragging) return;
  isDragging = false;
  const x = e.type.includes('mouse') ? e.clientX : e.changedTouches[0].clientX;
  const diff = x - startX;
  papers[currentIndex].style.transform = '';
  if (diff < -80) next();
  else if (diff > 80) prev();
}

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') prev();
  if (e.key === 'ArrowRight') next();
});

async function init() {
  try {
    const index = await loadIndex();
    const stack = document.getElementById('stack');
    const dots = document.getElementById('dots');
    
    for (let i = 0; i < index.dates.length; i++) {
      const data = await loadDay(index.dates[i]);
      const paper = renderPaper(data, i);
      stack.appendChild(paper);
      papers.push(paper);
      
      const dot = document.createElement('div');
      dot.className = 'nav-dot';
      dot.onclick = () => goTo(i);
      dots.appendChild(dot);
    }
    
    document.getElementById('prevBtn').onclick = prev;
    document.getElementById('nextBtn').onclick = next;
    
    stack.addEventListener('mousedown', handleStart);
    stack.addEventListener('mousemove', handleMove);
    stack.addEventListener('mouseup', handleEnd);
    stack.addEventListener('mouseleave', handleEnd);
    
    stack.addEventListener('touchstart', handleStart);
    stack.addEventListener('touchmove', handleMove);
    stack.addEventListener('touchend', handleEnd);
    
    updatePositions();
  } catch (err) {
    console.error('Init error:', err);
  }
}

init();
