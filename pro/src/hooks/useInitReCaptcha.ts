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
      }
    }
  }, [])
}
