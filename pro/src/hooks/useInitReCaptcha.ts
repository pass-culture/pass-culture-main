import { useEffect } from 'react'

import { initReCaptchaScript } from 'utils/recaptcha'

export const useInitReCaptcha = (): void => {
  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      gcaptchaScript.remove()
    }
  }, [])
}
