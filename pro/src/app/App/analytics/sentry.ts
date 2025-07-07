import * as Sentry from '@sentry/browser'
import {
  reactRouterV7BrowserTracingIntegration,
  replayIntegration,
} from '@sentry/react'
import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from 'react-router'

import { selectCurrentUser } from 'commons/store/user/selectors'
import {
  ENVIRONMENT_NAME,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
} from 'commons/utils/config'

import config from '../../../../package.json'

export const initializeSentry = () => {
  Sentry.init({
    dsn: SENTRY_SERVER_URL,
    environment: ENVIRONMENT_NAME,
    release: config.version,
    integrations: [
      reactRouterV7BrowserTracingIntegration({
        useEffect: useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes,
      }),
      replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    tracesSampleRate: parseFloat(SENTRY_SAMPLE_RATE),
    beforeSend: (event, hint) => {
      // To ignore a google recaptcha issue
      // and Google analytics issue
      if (
        hint.originalException === 'Timeout' ||
        hint.originalException === 'Timeout (u)'
      ) {
        return null
      }
      return event
    },
    // List of common errors to ignore
    // https://docs.sentry.io/platforms/javascript/configuration/filtering/#decluttering-sentry
    ignoreErrors: [
      // Random plugins/extensions
      '_avast_submit',
      'window.norton',
      'top.GLOBALS',
      '__AutoFillPopupClose__', // create by a random chinese web extension for mobile safari
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
      // See https://stackoverflow.com/questions/49384120/resizeobserver-loop-limit-exceeded/50387233#50387233
      'ResizeObserver loop limit exceeded',
      'ResizeObserver loop completed with undelivered notifications',
      // Firebase fails install when user lost connectivity for a moment
      'Could not process request. Application offline',
      // Error when Outlook scans a link
      // https://github.com/getsentry/sentry-javascript/issues/3440
      'Non-Error promise rejection captured with value: Object Not Found Matching Id',
      // Network errors, we already handle them in the SWR config by retrying and
      // showing a toaster message
      'Failed to fetch', // Chrome
      'NetworkError when attempting to fetch resource', // Firefox
      'Load failed', // Safari
      // Other network errors
      'La connexion réseau a été perdue',
      'A request was aborted',
    ],
    denyUrls: [
      // Facebook flakiness
      /graph\.facebook\.com/i,
      // Facebook blocked
      /connect\.facebook\.net\/en_US\/all\.js/i,
      // Woopra flakiness
      /eatdifferent\.com\.woopra-ns\.com/i,
      /static\.woopra\.com\/js\/woopra\.js/i,
      // Browser extensions
      /extensions\//i,
      /^chrome:\/\//i,
      /^chrome-extension:\/\//i,
      /safari-(web-)?extension:/i,
      /webkit-masked-url:/i,
      /<unknown module>/i,
      // Other plugins
      /127\.0\.0\.1:4001\/isrunning/i, // Cacaoweb
      /webappstoolbarba\.texthelp\.com\//i,
      /metrics\.itunes\.apple\.com\.edgesuite\.net\//i,
    ],
  })
}

export const useSentry = () => {
  const currentUser = useSelector(selectCurrentUser)

  useEffect(() => {
    if (currentUser && currentUser.id) {
      Sentry.setUser({ id: currentUser.id.toString() })
    }
  }, [currentUser])
}
