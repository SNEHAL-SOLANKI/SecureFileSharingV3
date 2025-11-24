document.addEventListener('DOMContentLoaded', function() {

  // ================================
  // Share button handling
  // ================================
  document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const link = btn.getAttribute('data-link');
      const modal = new bootstrap.Modal(document.getElementById('shareModal'));
      document.getElementById('shareLink').value = link;
      modal.show();
    });
  });

  // ================================
  // Copy button handling
  // ================================
  const copyBtn = document.getElementById('copyBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', function() {
      const input = document.getElementById('shareLink');
      input.select();
      navigator.clipboard.writeText(input.value).then(() => {
        copyBtn.innerText = 'Copied!';
        setTimeout(() => copyBtn.innerText = 'Copy', 1500);
      });
    });
  }

  // ================================
  // 🌟 STEP 7 — Fade-in Animation for Home Page
  // ================================
  document.querySelectorAll(".fade-in").forEach((el, i) => {
    setTimeout(() => el.classList.add("visible"), i * 120);
  });

});
