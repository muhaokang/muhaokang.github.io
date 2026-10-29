(() => {
  const input = document.querySelector('#post-search');
  if (!input) return;
  const rows = [...document.querySelectorAll('[data-post]')];
  const years = [...document.querySelectorAll('[data-year]')];
  const status = document.querySelector('#search-status');
  const empty = document.querySelector('#search-empty');
  document.querySelector('#archive-tools').hidden = false;
  input.addEventListener('input', () => {
    const words = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    rows.forEach(row => {
      const text = row.dataset.search.toLocaleLowerCase();
      row.hidden = !words.every(word => text.includes(word));
      if (!row.hidden) count += 1;
    });
    years.forEach(year => { year.hidden = !year.querySelector('[data-post]:not([hidden])'); });
    status.textContent = words.length ? '找到 ' + count + ' 篇文章' : '共 ' + rows.length + ' 篇文章';
    empty.hidden = count > 0;
  });
})();
