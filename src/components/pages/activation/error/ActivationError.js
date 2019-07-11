/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import MailToLink from '../../../layout/MailToLink'
import { SUPPORT_EMAIL, SUPPORT_EMAIL_SUBJECT } from '../../../../utils/config'

const ActivationError = () => {
  const emailHeaders = {
    subject: decodeURI(SUPPORT_EMAIL_SUBJECT),
  }
  return (
    <main
      className="pc-main padded-2x flex-rows flex-center"
      id="activation-error-page"
      role="main"
    >
      <div className="flex-center flex-row">
        <p className="fs20">{'Il semblerait que le lien cliqué soit incorrect.'}</p>
      </div>

      <div className="flex-center flex-row padded">
        <MailToLink
          className="no-background border-all rd4 py12 px18 is-inline-block is-white-text text-center fs16"
          email={SUPPORT_EMAIL}
          headers={emailHeaders}
          id="activation-error-contact-us"
          obfuscate
        >
          <span>{'Contactez-nous'}</span>
        </MailToLink>
      </div>
    </main>
  )
}

export default ActivationError
