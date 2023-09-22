import { useEffect } from 'react'

import { initReCaptchaScript } from 'utils/recaptcha'

const useInitReCaptcha = (): void => {
  useEffect(() => {
    const gcaptchaScript = initReCaptchaScript()

    return function cleanup() {
      gcaptchaScript.remove()
    }
  }, [])
}

export default useInitReCaptcha
