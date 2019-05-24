const MATOMO_SERVER_URL = process.env.MATOMO_SERVER_URL

function initMatomo() {
  if (!MATOMO_SERVER_URL) {
    return
  }

  const _paq = window._paq || []
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['enableLinkTracking'])
  ;(function() {
    _paq.push(['setTrackerUrl', `${MATOMO_SERVER_URL}/matomo.php`])
    _paq.push(['setSiteId', '1'])
    const d = document
    const g = d.createElement('script')
    const s = d.getElementsByTagName('script')[0]
    g.type = 'text/javascript'
    g.async = true
    g.defer = true
    g.src = `${MATOMO_SERVER_URL}matomo.js`
    s.parentNode.insertBefore(g, s)
  })()
}

initMatomo()
