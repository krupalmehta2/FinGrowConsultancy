(() => {
 const panel = document.querySelector('#fg-user-stats'); if (!panel) return;
 const button = panel.querySelector('[data-refresh-stats]'); const message = panel.querySelector('[data-stats-message]'); let loading = false;
 async function refresh() { if (loading) return; loading = true; button.disabled = true; button.textContent = 'Loading...'; message.textContent = 'Loading...'; try { const response = await fetch(panel.dataset.statsUrl, {headers: {'X-Requested-With': 'XMLHttpRequest'}}); if (!response.ok) throw new Error(); const stats = await response.json(); Object.entries(stats).forEach(([key, value]) => { const target = panel.querySelector(`[data-stat="${key}"]`); if (target) target.textContent = value; }); message.textContent = 'Data loaded.'; } catch (error) { message.textContent = 'Unable to load data. Please try again.'; } finally { loading = false; button.disabled = false; button.textContent = 'Refresh'; } }
 button.addEventListener('click', refresh);
})();