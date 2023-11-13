import { init as SentryInit } from '@sentry/browser'
import * as Sentry from '@sentry/react'
import { Integrations as TracingIntegrations } from '@sentry/tracing'
import React from 'react'
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from 'react-router-dom'

import {
  ENVIRONMENT_NAME,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
} from 'utils/config'

import config from '../package.json'

export const initializeSentry = () => {
  SentryInit({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: config.version,
    integrations: [
      new TracingIntegrations.BrowserTracing({
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
    // List of common errors to ignore
    // https://docs.sentry.io/platforms/javascript/configuration/filtering/#decluttering-sentry
    ignoreErrors: [
      // Browser extensions
      'webkit-masked-url://hidden/',
      'safari-web-extension://',
      '_avast_submit',
      '?(<unknown module>)',
      'beamer-embed',
      // Random plugins/extensions
      'top.GLOBALS',
      // See: http://blog.errorception.com/2012/03/tale-of-unfindable-js-error.html
      'originalCreateNotification',
      'canvas.contentDocument',
      'MyApp_RemoveAllHighlights',
      'http://tt.epicplay.com',
      "Can't find variable: ZiteReader",
      'jigsaw is not defined',
      'ComboSearch is not defined',
      'http://loading.retry.widdit.com/',
      'atomicFindClose',
      // Facebook borked
      'fb_xd_fragment',
      // ISP "optimizing" proxy - `Cache-Control: no-transform` seems to
      // reduce this. (thanks @acdha)
      // See http://stackoverflow.com/questions/4113268
      'bmi_SafeAddOnload',
      'EBCallBackMessageReceived',
      // See http://toolbar.conduit.com/Developer/HtmlAndGadget/Methods/JSInjection.aspx
      'conduitPage',
    ],
    denyUrls: [
      // Facebook flakiness
      /graph\.facebook\.com/i,
      // Facebook blocked
      /connect\.facebook\.net\/en_US\/all\.js/i,
      // Woopra flakiness
      /eatdifferent\.com\.woopra-ns\.com/i,
      /static\.woopra\.com\/js\/woopra\.js/i,
      // Chrome extensions
      /extensions\//i,
      /^chrome:\/\//i,
      /^chrome-extension:\/\//i,
      // Other plugins
      /127\.0\.0\.1:4001\/isrunning/i, // Cacaoweb
      /webappstoolbarba\.texthelp\.com\//i,
      /metrics\.itunes\.apple\.com\.edgesuite\.net\//i,
    ],
  })
}
