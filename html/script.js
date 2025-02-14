document.addEventListener('DOMContentLoaded', function() {
  // Add search functionality
  const searchInput = document.getElementById('searchInput');
  const birdEntries = document.querySelectorAll('.card');

  searchInput.addEventListener('input', function() {
    const query = searchInput.value.toLowerCase();
    birdEntries.forEach(function(entry) {
      const birdName = entry.querySelector('h3').textContent.toLowerCase();
      if (birdName.includes(query)) {
        entry.style.display = 'block';
      } else {
        entry.style.display = 'none';
      }
    });
  });

  // Add collapsible sections
  const collapsibleHeaders = document.querySelectorAll('.collapsible');
  collapsibleHeaders.forEach(function(header) {
    header.addEventListener('click', function() {
      const content = header.nextElementSibling;
      if (content.style.display === 'block') {
        content.style.display = 'none';
      } else {
        content.style.display = 'block';
      }
    });
  });
});