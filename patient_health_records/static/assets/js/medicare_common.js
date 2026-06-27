/* =============================================
   MediCare — Shared JS for All Dashboards
   Used by: admin, doctor, patient dashboards
   ============================================= */

/**
 * Show a content section and mark the sidebar link active.
 * Doctor dashboard OVERRIDES this (to also stop QR scanner).
 * @param {string} sectionId  - id of the section div
 * @param {Element|null} el   - the sidebar-link element that was clicked
 */
function showSection(sectionId, el) {
  document
    .querySelectorAll(".content-section")
    .forEach((s) => s.classList.remove("active"));
  document.getElementById(sectionId).classList.add("active");

  document
    .querySelectorAll(".sidebar-link")
    .forEach((l) => l.classList.remove("active"));
  if (el) el.classList.add("active");

  const main = document.getElementById("mainContent");
  if (main) main.scrollTo({ top: 0, behavior: "smooth" });

  if (window.innerWidth < 768) {
    document.getElementById("sidebarMenu").classList.remove("show");
  }
}

/** Toggle mobile sidebar visibility. */
function toggleSidebar() {
  document.getElementById("sidebarMenu").classList.toggle("show");
}

/** Close sidebar when clicking outside on mobile. */
document.addEventListener("click", function (e) {
  const sidebar = document.getElementById("sidebarMenu");
  const btn = document.querySelector(".mobile-toggle");
  if (
    window.innerWidth < 768 &&
    sidebar &&
    sidebar.classList.contains("show") &&
    !sidebar.contains(e.target) &&
    btn &&
    !btn.contains(e.target)
  ) {
    sidebar.classList.remove("show");
  }
});

/** Auto-dismiss Bootstrap alerts after 5 seconds. */
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    document.querySelectorAll(".alert").forEach(function (a) {
      try {
        new bootstrap.Alert(a).close();
      } catch (e) {}
    });
  }, 5000);
});
