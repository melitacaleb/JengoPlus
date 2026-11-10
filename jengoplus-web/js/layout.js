/* SHELL: edit NAV / FOOTER once here and every page updates. */
(function(){var t;try{t=localStorage.getItem('jp-theme')}catch(e){}
t=t||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');document.documentElement.setAttribute('data-bs-theme',t)})();
const NAV=[{href:'index.html',label:'Home',page:'home'},{href:'index.html#modules',label:'Modules'},{href:'index.html#how',label:'How it works'},
 {href:'supervisor.html',label:'Supervisor',page:'sup'},{href:'admin.html',label:'Administrator',page:'admin'}];
document.addEventListener('DOMContentLoaded',()=>{
 const pg=document.body.dataset.page||'';
 const h=document.getElementById('site-header');
 if(h)h.innerHTML=`<nav class="navbar navbar-expand-lg jp-nav sticky-top"><div class="container">
 <a class="navbar-brand" href="index.html"><span class="logo"><i class="bi bi-bricks"></i></span>Jengo<b>Plus</b></a>
 <button class="btn-icon d-lg-none" data-bs-toggle="collapse" data-bs-target="#nv" aria-label="Menu"><i class="bi bi-list fs-4"></i></button>
 <div id="nv" class="collapse navbar-collapse"><ul class="navbar-nav ms-lg-4 me-auto">
 ${NAV.map(n=>`<li class="nav-item"><a class="nav-link ${n.page===pg?'active':''}" href="${n.href}">${n.label}</a></li>`).join('')}</ul>
 <div class="d-flex gap-2 py-2 py-lg-0"><button id="themeBtn" class="btn-icon" aria-label="Switch between light and dark mode" title="Light / dark"></button>
 <a class="btn btn-jp d-flex align-items-center" href="login.html">Sign in</a></div></div></div></nav>`;
 const f=document.getElementById('site-footer');
 if(f)f.innerHTML=`<footer><div class="container d-md-flex justify-content-between gap-4"><div><div class="navbar-brand">Jengo<b>Plus</b></div>
 <p class="text-mute small mb-0">Workforce and expense control for construction sites.<br>&copy; ${new Date().getFullYear()} TriadCore Technologies</p></div>
 <div class="mt-3 mt-md-0"><a href="supervisor.html">Supervisor portal</a><a href="admin.html">Administrator portal</a><a href="login.html">Sign in</a></div></div></footer>`;
 const btn=document.getElementById('themeBtn');
 const paint=()=>{const d=document.documentElement.dataset.bsTheme==='dark';if(btn)btn.innerHTML=`<i class="bi ${d?'bi-sun-fill':'bi-moon-stars-fill'}"></i>`};
 paint();
 btn&&btn.addEventListener('click',()=>{const n=document.documentElement.dataset.bsTheme==='dark'?'light':'dark';
  document.documentElement.dataset.bsTheme=n;try{localStorage.setItem('jp-theme',n)}catch(e){}paint()});
});
window.jpToast=(msg)=>{let c=document.getElementById('toasts');if(!c){c=document.createElement('div');c.id='toasts';c.className='toast-container position-fixed bottom-0 end-0 p-3';document.body.appendChild(c)}
 const e=document.createElement('div');e.className='toast align-items-center text-bg-dark border-0 show';e.innerHTML=`<div class="d-flex"><div class="toast-body">${msg}</div></div>`;c.appendChild(e);setTimeout(()=>e.remove(),3500)};
