import './styles/index.scss'
import React from 'react'
import { createRoot } from 'react-dom/client'

import { initializeSentry } from 'app/App/analytics/sentry'
import { Root } from 'Root'
import { SENTRY_SERVER_URL } from 'utils/config'

import { unregister } from './registerServiceWorker'

const isAdageIframe = window.location.href.includes('adage-iframe')

// Initialize sentry
if (SENTRY_SERVER_URL) {
  initializeSentry()
}

// load and initialise hotjar library for all pc pro except adage-iframe
// included in the bundle instead of <script> tag in index.html
// to avoid the need of 'insafe-inline' in Content Security Policy
if (!isAdageIframe) {
  ;(function (h: any, o, t, j, a?: any, r?: any) {
    h.hj =
      h.hj ||
      function () {
        // eslint-disable-next-line prefer-rest-params
        ;(h.hj.q = h.hj.q || []).push(arguments)
      }
    h._hjSettings = {
      hjid: 2925982,
      hjsv: 6,
    }
    a = o.getElementsByTagName('head')[0]
    r = o.createElement('script')
    r.async = 1
    r.setAttribute('data-src', t + h._hjSettings.hjid + j + h._hjSettings.hjsv)
    r.setAttribute('data-type', 'application/javascript')
    r.setAttribute('data-name', 'hotjar')
    r.type = 'opt-in'
    a.appendChild(r)
  })(window, document, 'https://static.hotjar.com/c/hotjar-', '.js?sv=')
}

// Start app
// @ts-expect-error
const root = createRoot(document.getElementById('root'))

root.render(
  <React.StrictMode>
    <Root isAdageIframe={isAdageIframe} />
  </React.StrictMode>
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
unregister()

// Reloads page when a dynamic import fails (when we release a new version)
// https://vitejs.dev/guide/build#load-error-handling
window.addEventListener('vite:preloadError', (event) => {
  event.preventDefault()
  window.location.reload()
})
