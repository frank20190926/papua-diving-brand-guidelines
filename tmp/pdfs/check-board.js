(() => {
 document.body.style.zoom = '0.6';
 const board=document.querySelector('.board'), base=board.getBoundingClientRect();
 const errors=[];
 for(const node of document.querySelectorAll('h1,h2,h3,p,header,footer,a')) {
  const r=node.getBoundingClientRect();
  if(r.right>base.right+1||r.bottom>base.bottom+1||r.left<base.left-1) errors.push({text:node.textContent.slice(0,80),rect:[r.x,r.y,r.width,r.height]});
 }
 return JSON.stringify({title:document.title,layout:[board.offsetWidth,board.offsetHeight],fonts:document.fonts.status,missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),overflow:errors,viewport:[innerWidth,innerHeight],outer:[outerWidth,outerHeight]});
})();
