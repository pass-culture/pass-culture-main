const { MATOMO_SERVER_URL } = process.env

const _paq = window._paq || []
_paq.push(['enableLinkTracking'])

const initMatomo = () => {
  if (!MATOMO_SERVER_URL) {
    return
  }
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
}

export default initMatomo
