import './styles/index.scss'

import React from 'react'
import { createRoot } from 'react-dom/client'

import { initializeSentry } from '@/app/App/analytics/sentry'
import { SENTRY_SERVER_URL } from '@/commons/utils/config'

import { Root } from 'Root'
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
  if (import.meta.env.MODE !== 'development') {
    // biome-ignore lint/suspicious/noExplicitAny: Hotjar script.
    ;((h: any, o, t, j, a?: any, r?: any, tmpl?: any) => {
      h.hj =
        h.hj ||
        (() => {
          // @ts-expect-error
          // biome-ignore lint: Dubious (`arguments` doesn't exist in arrow functions) but this an external library.
          ;(h.hj.q = h.hj.q || []).push(arguments)
        })
      h._hjSettings = {
        hjid: 2925982,
        hjsv: 6,
      }
      a = o.getElementsByTagName('head')[0]
      tmpl = o.createElement('template')
      tmpl.setAttribute('data-purpose', 'hotjar')
      r = o.createElement('script')
      r.async = 1
      r.src = t + h._hjSettings.hjid + j + h._hjSettings.hjsv
      tmpl.content.appendChild(r)
      a.appendChild(tmpl)
    })(window, document, 'https://static.hotjar.com/c/hotjar-', '.js?sv=')
  }
  // We do the same thing for orejime scripts
  ;((d, v, prefix) => {
    const head = d.getElementsByTagName('head')[0]
    const script = d.createElement('script')
    script.src = `${prefix}${v}/dist/orejime-standard-fr.js`
    head.appendChild(script)
    const link = d.createElement('link')
    link.rel = 'stylesheet'
    link.href = `${prefix}${v}/dist/orejime-standard.css`
    link.crossOrigin = 'anonymous'
    head.appendChild(link)
  })(document, '3.1.0', 'https://cdn.jsdelivr.net/npm/orejime@')
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
