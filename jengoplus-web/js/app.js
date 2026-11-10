/* Page behaviour (demo data only; replace with Django views/API calls later). */
document.addEventListener('DOMContentLoaded',()=>{
 // Attendance: tap a worker -> camera opens -> photo required to mark present
 const grid=document.getElementById('workerGrid');
 if(grid){const planned=+grid.dataset.planned||10;
  const upd=()=>{const n=grid.querySelectorAll('.present').length;
   document.getElementById('count').textContent=n;const b=document.getElementById('bar');
   b.style.width=Math.min(100,n/planned*100)+'%';b.classList.toggle('over',n>planned);
   document.getElementById('over').classList.toggle('d-none',n<=planned)};
  grid.querySelectorAll('.tile').forEach(t=>{const f=t.querySelector('input');
   t.addEventListener('click',()=>{ if(t.classList.contains('present')){t.classList.remove('present');t.querySelector('img')?.remove();f.value='';upd()}else f.click()});
   f.addEventListener('click',e=>e.stopPropagation());
   f.addEventListener('change',()=>{if(!f.files[0])return;const i=document.createElement('img');i.alt='';i.src=URL.createObjectURL(f.files[0]);
    t.prepend(i);t.classList.add('present');upd();jpToast('Photo saved for '+t.dataset.name)})});
  document.getElementById('submitAtt').addEventListener('click',()=>{const n=grid.querySelectorAll('.present').length;
   n?jpToast('Attendance submitted: '+n+' workers'):jpToast('Mark at least one worker first')});upd()}
 // Claims: approve / reject (reject needs a reason)
 document.querySelectorAll('[data-claim]').forEach(b=>b.addEventListener('click',()=>{
  const row=b.closest('tr');let ok=b.dataset.claim==='approve',reason='';
  if(!ok){reason=prompt('Reason for rejecting this claim?');if(!reason)return jpToast('A reason is required to reject')}
  row.querySelector('.st').innerHTML=ok?'<span class="badge text-bg-success">Approved</span>':'<span class="badge text-bg-danger">Rejected</span>';
  row.querySelector('.act').innerHTML='<span class="text-mute small">'+(ok?'Approved by you':reason)+'</span>';jpToast(ok?'Claim approved':'Claim rejected')}));
 // Generic demo forms
 document.querySelectorAll('form[data-demo]').forEach(f=>f.addEventListener('submit',e=>{e.preventDefault();
  if(f.dataset.demo==='login'){location.href=f.querySelector('[name=role]:checked').value;return}
  jpToast(f.dataset.msg||'Saved');f.reset()}));
 document.getElementById('showPw')?.addEventListener('click',()=>{const p=document.getElementById('pw');p.type=p.type==='password'?'text':'password'});
});
