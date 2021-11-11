export default () => {
  setTimeout(() => {
    window._paq.push(['setCustomUrl', window.location])
    window._paq.push(['setDocumentTitle', document.title])
    window._paq.push(['trackPageView'])
  }, 0)
}
