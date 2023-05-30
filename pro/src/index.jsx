import './styles/index.scss'
// import { init as SentryInit } from '@sentry/browser'
import React from 'react'
import { createRoot } from 'react-dom/client'
import smoothscroll from 'smoothscroll-polyfill'

import { unregister } from './registerServiceWorker'
import Root from './Root'
import { initCookieConsent } from './utils/cookieConsentModal'

// // Initialize sentry
// if (SENTRY_SERVER_URL) {
//   SentryInit({
//     dsn: SENTRY_SERVER_URL,
//     environment: ENVIRONMENT_NAME,
//     release: config.version,
//     integrations: [
//       new TracingIntegrations.BrowserTracing({
//         routingInstrumentation: Sentry.reactRouterV6Instrumentation(
//           React.useEffect,
//           useLocation,
//           useNavigationType,
//           createRoutesFromChildren,
//           matchRoutes
//         ),
//       }),
//     ],
//     tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
//   })
// }

// Initialize cookie consent modal
initCookieConsent()

// load and initialise hotjar library
// included in the bundle instead of <script> tag in index.html
// to avoid the need of 'insafe-inline' in Content Security Policy
;(function (h, o, t, j, a, r) {
  h.hj =
    h.hj ||
    function () {
      ;(h.hj.q = h.hj.q || []).push(arguments)
    }
  h._hjSettings = {
    hjid: 2925982,
    hjsv: 6,
  }
  a = o.getElementsByTagName('head')[0]
  r = o.createElement('script')
  r.async = 1
  r['data-src'] = t + h._hjSettings.hjid + j + h._hjSettings.hjsv
  r['type'] = 'opt-in'
  r['data-type'] = 'application/javascript'
  r['data-name'] = 'hotjar'
  a.appendChild(r)
})(window, document, 'https://static.hotjar.com/c/hotjar-', '.js?sv=')

smoothscroll.polyfill()

// Start app
const root = createRoot(document.getElementById('root'))
root.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
unregister()
