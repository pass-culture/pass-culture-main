import { useEffect } from 'react'

import { isError } from '@/apiClient/helpers'
import { RECAPTCHA_SITE_KEY } from '@/commons/utils/config'
import { initReCaptchaScript } from '@/commons/utils/recaptcha'

export const useInitReCaptcha = (): void => {
  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      // Can be undefined according to sentry errors
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      if (gcaptchaScript) {
        try {
          if (window.grecaptcha) {
            window.grecaptcha.reset?.(RECAPTCHA_SITE_KEY)
          }
        } catch (e) {
          if (
            isError(e) &&
            (e.message.includes('Method not found') ||
              e.message.includes('Uncaught (in promise) Timeout'))
          ) {
            // This happens for Android 13/14 devices
          } else {
            // Rethrow the error
            throw e
          }
        }
        gcaptchaScript.remove()

        // Remove all the widgets already added
        const widgets = document.getElementsByClassName('grecaptcha-badge')
        for (const widget of widgets) {
          const parent = widget.parentElement
          if (parent) {
            parent.remove()
          } else {
            widget.remove()
          }
        }
      }
    }
  }, [])
}
