// Auto-dismiss alerts
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert && bsAlert.close();
    }, 5000);
  });
});
