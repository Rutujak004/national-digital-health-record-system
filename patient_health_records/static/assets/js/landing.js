/* =============================================
   MediCare — Landing Page JS
============================================= */

document.addEventListener("DOMContentLoaded", function () {
  // ── AOS Init ──
  if (typeof AOS !== "undefined") {
    AOS.init({ once: true, duration: 650, offset: 60 });
  }

  // ── Navbar scroll shadow ──
  const header = document.getElementById("main-header");
  window.addEventListener("scroll", function () {
    if (window.scrollY > 20) {
      header.style.boxShadow = "0 4px 24px rgba(0,0,0,0.08)";
    } else {
      header.style.boxShadow = "none";
    }
  });

  // ── Active nav link on scroll ──
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-link-item");
  window.addEventListener("scroll", function () {
    let current = "";
    sections.forEach((section) => {
      const top = section.offsetTop - 100;
      if (window.scrollY >= top) current = section.getAttribute("id");
    });
    navLinks.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === "#" + current)
        link.classList.add("active");
    });
  });

  // ── Scroll top button ──
  const scrollBtn = document.getElementById("scroll-top");
  if (scrollBtn) {
    window.addEventListener("scroll", function () {
      scrollBtn.classList.toggle("visible", window.scrollY > 300);
    });
    scrollBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ── Smooth scroll for all anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
});

// ── Mobile nav toggle ──
function toggleMobileNav() {
  const nav = document.getElementById("mobileNav");
  const icon = document.getElementById("mobileIcon");
  const isOpen = nav.classList.contains("open");
  nav.classList.toggle("open", !isOpen);
  icon.className = isOpen ? "bi bi-list" : "bi bi-x-lg";
}

function closeMobileNav() {
  const nav = document.getElementById("mobileNav");
  const icon = document.getElementById("mobileIcon");
  nav.classList.remove("open");
  icon.className = "bi bi-list";
}
