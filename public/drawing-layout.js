document.querySelectorAll('.sheet-size').forEach(button=>{
  const sheet=button.closest('.drawing-sheet');
  const title=sheet.querySelector('figcaption>span').textContent;
  button.hidden=false;
  button.addEventListener('click',()=>{
    const expanded=sheet.classList.toggle('is-expanded');
    button.setAttribute('aria-expanded',String(expanded));
    button.setAttribute('aria-label',`${expanded?'Reduce':'Enlarge'} ${title}`);
    button.textContent=expanded?'Reduce ↙':'Enlarge ↗';
    if(!expanded)sheet.scrollIntoView({block:'nearest',behavior:'instant'});
  });
});
