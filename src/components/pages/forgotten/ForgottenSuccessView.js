/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import { InputField } from '../../forms/inputs'
import NavigationFooter from '../../layout/NavigationFooter'

const ForgottenSuccessPage = () => (
  <div
    id="forgotten-password-success"
    className="page is-relative pc-gradient flex-rows"
  >
    <main role="main" className="pc-main flex-rows flex-center flex-1">
      <div className="padded">
        <h2 className="mb36 is-white-text">
          <span className="is-block is-italic is-medium fs22">
            Renseignez votre adresse e-mail pour réinitialiser votre mot de
            passe.
          </span>
          <span className="is-block is-regular fs13 mt18">
            <span className="is-white-text">*</span>
            &nbsp;Champs obligatoires
          </span>
        </h2>
      </div>
    </main>
    <NavigationFooter theme="transparent" className="dotted-top-white" />
  </div>
)

export default ForgottenSuccessPage
