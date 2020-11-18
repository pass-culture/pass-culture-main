import { RECAPTCHA_SITE_KEY } from './config'

export const initReCaptchaScript = () => {
  const script = document.createElement('script')

  script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`
  script.async = true

  document.body.appendChild(script)

  return () => {
    document.body.removeChild(script)
  }
}

export const destroyReCaptchaScript = () => {
  const scriptTag = document.querySelector(
    'script[src="https://www.google.com/recaptcha/api.js?render=recaptcha-site-key"]'
  )

  document.body.removeChild(scriptTag)
}

export const getReCaptchaToken = action =>
  new Promise(resolve =>
    window.grecaptcha.ready(function () {
      console.log(RECAPTCHA_SITE_KEY)
      window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action }).then(function (token) {
        resolve(token)
      })
    })
  )
