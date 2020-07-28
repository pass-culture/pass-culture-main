import React, { Fragment } from 'react'

export const RecaptchaNotice = () => (
  <Fragment>
    <div className="recaptcha-notice">
      {'Ce site est protégé par reCAPTCHA Google.'}
    </div>
    <div className="recaptcha-notice">
      {'La '}
      <a
        href="https://policies.google.com/privacy"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Charte des Données Personnelles'}
      </a>
      {' et les '}
      <a
        href="https://policies.google.com/terms"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Conditions Générales d’Utilisation'}
      </a>
      {' s’appliquent.'}
    </div>
  </Fragment>
)
