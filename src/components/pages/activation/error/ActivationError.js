/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import MailToLink from '../../../layout/MailToLink'
import { SUPPORT_EMAIL } from '../../../../utils/config'

const ActivationError = () => (
  <main
    role="main"
    id="activation-error-page"
    className="pc-main padded-2x flex-rows flex-center"
  >
    <h2 className="fs20">Il semblerait que le lien cliqué soit incorrect.</h2>
    <p className="fs20">
      <MailToLink
        obfuscate
        email={SUPPORT_EMAIL}
        id="activation-error-contact-us"
        className="is-underline is-block is-white-text py12"
      >
        <span>Contactez-nous</span>
      </MailToLink>
    </p>
  </main>
)
export default ActivationError
