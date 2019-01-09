/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import MailToLink from '../../../layout/MailToLink'
import { SUPPORT_EMAIL } from '../../../../utils/config'

const MyComponent = () => (
  <div className="mb36">
    <div className="mb36">
      <MailToLink
        obfuscate
        email={SUPPORT_EMAIL}
        id="activation-events-contact-us"
        className="is-block text-center button is-rounded py7 no-background"
      >
        <span className="fs18 is-white-text is-bold">
          Activation par e-mail
        </span>
      </MailToLink>
    </div>
    <div className="text-center">
      <span className="is-italic is-medium fs20">--&nbsp;ou&nbsp;--</span>
    </div>
  </div>
)
MyComponent.defaultProps = {}
MyComponent.propTypes = {}
export default MyComponent
