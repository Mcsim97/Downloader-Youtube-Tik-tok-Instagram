const form = document.getElementById('download-form');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const urlInput = document.getElementById('url');
const useCookies = document.getElementById('useCookies');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  resultEl.classList.add('hidden');
  statusEl.classList.remove('hidden');
  statusEl.textContent = '⏳ Скачиваем... (подожди, это может занять время)';

  const payload = {
    url: urlInput.value.trim(),
    useCookies: useCookies.checked
  };

  try {
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!data.ok) {
      throw new Error(data.error || 'Неизвестная ошибка');
    }

    statusEl.textContent = '✅ Готово!';
    resultEl.classList.remove('hidden');
    resultEl.innerHTML = `Файл: <strong>${data.filename}</strong><br/><a href="${data.downloadUrl}">Скачать</a>`;
  } catch (err) {
    statusEl.textContent = `❌ Ошибка: ${err.message}`;
  }
});

