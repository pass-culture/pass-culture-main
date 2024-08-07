import { useEffect } from 'react'

import { initReCaptchaScript } from 'utils/recaptcha'

export const useInitReCaptcha = (): void => {
  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      // Can be undefined according to sentry errors
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      if (gcaptchaScript) {
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
