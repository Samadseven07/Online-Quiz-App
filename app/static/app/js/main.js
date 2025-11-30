// ===== Delete Confirmation Modal =====
document.addEventListener('DOMContentLoaded', function () {
  // Handle delete buttons with data-confirm-delete
  document.querySelectorAll('[data-confirm-delete]').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const title = this.dataset.title || 'this item';
      const url = this.getAttribute('href');

      // Create modal
      const overlay = document.createElement('div');
      overlay.className = 'delete-modal-overlay';
      overlay.innerHTML = `
        <div class="delete-modal">
          <h3>Delete Confirmation</h3>
          <p>Are you sure you want to delete "${title}"?</p>
          <div class="delete-modal-actions">
            <button class="delete-modal-btn delete-modal-btn-cancel">Cancel</button>
            <button class="delete-modal-btn delete-modal-btn-confirm">Yes, Delete</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      // Close on Cancel
      overlay.querySelector('.delete-modal-btn-cancel').addEventListener('click', () => {
        document.body.removeChild(overlay);
      });

      // Close on click outside
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          document.body.removeChild(overlay);
        }
      });

      // Confirm delete (POST to avoid CSRF issues)
      overlay.querySelector('.delete-modal-btn-confirm').addEventListener('click', () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;

        // Add CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value || 
                          document.querySelector('input[name="csrfmiddlewaretoken"]').value ||
                          '{{ csrf_token }}'.replace(/ /g, '');
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
      });
    });
  });
});