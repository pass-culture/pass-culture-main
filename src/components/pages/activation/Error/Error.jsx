import React from 'react'

import MailToLink from '../../../layout/MailToLink/MailToLink'
import { SUPPORT_EMAIL, SUPPORT_EMAIL_SUBJECT } from '../../../../utils/config'

const Error = () => {
  const emailHeaders = {
    subject: decodeURI(SUPPORT_EMAIL_SUBJECT),
  }

  return (
    <div className="logout-form-container error">
      <div>
        <p className="fs20 mb28">
          {'Il semblerait que le lien cliqué soit incorrect.'}
        </p>
        <MailToLink
          className="no-background border-all rd4 py12 px18 is-inline-block is-white-text text-center fs16"
          email={SUPPORT_EMAIL}
          headers={emailHeaders}
          obfuscate
        >
          <span>
            {'Contactez-nous'}
          </span>
        </MailToLink>
      </div>
    </div>
  )
}

export default Error
