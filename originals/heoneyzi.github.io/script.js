'use strict';
const languageToggle = document.querySelector('#language-toggle');
const translatedElements = [...document.querySelectorAll('[data-ko]')];
translatedElements.forEach(element => { element.dataset.en = element.innerHTML; });
function setLanguage(language) {
  const korean = language === 'ko';
  document.documentElement.lang = korean ? 'ko' : 'en';
  translatedElements.forEach(element => { element.innerHTML = korean ? element.dataset.ko : element.dataset.en; });
  languageToggle.textContent = korean ? 'EN' : 'KR';
  languageToggle.setAttribute('aria-label', korean ? 'View in English' : '한국어로 보기');
  try { localStorage.setItem('portfolio-language', korean ? 'ko' : 'en'); } catch {}
}
if (languageToggle) {
  languageToggle.hidden = false;
  languageToggle.addEventListener('click', () => setLanguage(document.documentElement.lang === 'ko' ? 'en' : 'ko'));
  try { if (localStorage.getItem('portfolio-language') === 'ko') setLanguage('ko'); } catch {}
}
