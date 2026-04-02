/* =========================
   COPY IBAN
========================= */

function copyIBAN(){

  const ibanEl = document.getElementById("iban");
  const msgEl = document.getElementById("copy-msg");

  if(!ibanEl || !msgEl) return;

  const iban = ibanEl.innerText.trim();

  navigator.clipboard.writeText(iban).then(() => {

    msgEl.textContent = "Copiato ✓";

    setTimeout(()=>{
      msgEl.textContent = "";
    },2000);

  });

}


/* =========================
   COUNTDOWN
========================= */

(function(){

  const el = document.querySelector(".countdown");

  if(!el) return;

  const targetDate = new Date(el.dataset.date);

  const daysEl = el.querySelector(".cd-days");
  const hoursEl = el.querySelector(".cd-hours");
  const minsEl = el.querySelector(".cd-minutes");
  const secsEl = el.querySelector(".cd-seconds");

  function pad(n){
    return n.toString().padStart(2,"0");
  }

  function update(){

    const now = new Date();
    const diff = targetDate - now;

    if(diff <= 0){
      clearInterval(timer);
      return;
    }

    const days = Math.floor(diff / (1000*60*60*24));
    const hours = Math.floor(diff / (1000*60*60) % 24);
    const mins = Math.floor(diff / (1000*60) % 60);
    const secs = Math.floor(diff / 1000 % 60);

    if(daysEl) daysEl.textContent = days;
    if(hoursEl) hoursEl.textContent = pad(hours);
    if(minsEl) minsEl.textContent = pad(mins);
    if(secsEl) secsEl.textContent = pad(secs);

  }

  update();

  const timer = setInterval(update,1000);

})();


document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll(".page");

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible"); // fade in
        } else {
          entry.target.classList.remove("visible"); // fade out
        }
      });
    },
    {
      threshold: 0.2 // triggers when 20% of section is visible
    }
  );

  sections.forEach(section => observer.observe(section));
});


document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".timeline-item");

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        } else {
          entry.target.classList.remove("visible");
        }
      });
    },
    { threshold: 0.3 }
  );

  items.forEach((item, index) => {
    // Add alternating left/right classes
    if (index % 2 === 1) item.classList.add("right");
    observer.observe(item);
  });
});

const menuToggle  = document.querySelector(".menu-toggle");
const menuOverlay = document.querySelector(".main-nav-overlay");
const menuClose   = document.querySelector(".menu-close");
const menuLinks   = document.querySelectorAll(".main-nav-overlay a");

if(menuToggle && menuOverlay){

  function openMenu(){
    menuOverlay.classList.add("open");
  }

  function closeMenu(){
    menuOverlay.classList.remove("open");
  }

  menuToggle.addEventListener("click", openMenu);

  if(menuClose){
    menuClose.addEventListener("click", closeMenu);
  }

  // close when clicking outside panel
  menuOverlay.addEventListener("click", (e) => {
    if(e.target === menuOverlay){
      closeMenu();
    }
  });

  // close when clicking link
  menuLinks.forEach(link => {
    link.addEventListener("click", closeMenu);
  });

}
