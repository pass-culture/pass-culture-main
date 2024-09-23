import { useEffect } from 'react'

import { RECAPTCHA_SITE_KEY } from 'utils/config'
import { initReCaptchaScript } from 'utils/recaptcha'

export const useInitReCaptcha = (): void => {
  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      // Can be undefined according to sentry errors
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      if (gcaptchaScript) {
        window.grecaptcha &&
          window.grecaptcha.reset &&
          window.grecaptcha.reset(RECAPTCHA_SITE_KEY)
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
