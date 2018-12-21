/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import MailToLink from '../../layout/MailToLink'
import { SUPPORT_EMAIL } from '../../../utils/config'

const ActivationError = () => (
  <div className="padded-2x flex-1 flex-rows flex-center">
    <h2 className="fs20">Il semblerait que le lien cliqué soit incorrect.</h2>
    <p className="fs20">
      <MailToLink
        obfuscate
        email={SUPPORT_EMAIL}
        id="activation-error-contact-us"
        className="no-underline is-block is-white-text py12"
      >
        <span className="is-underline">Contactez-nous</span>
      </MailToLink>
    </p>
  </div>
)
export default ActivationError
