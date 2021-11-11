import { RECAPTCHA_SITE_KEY } from './config'

export const initReCaptchaScript = () => {
  const script = document.createElement('script')

  script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`
  script.async = true

  return document.body.appendChild(script)
}

export const getReCaptchaToken = action =>
  new Promise(resolve =>
    window.grecaptcha.ready(function () {
      window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action }).then(function (token) {
        resolve(token)
      })
    })
  )
