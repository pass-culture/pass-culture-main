/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

const DEMARCHE_SIMPLIFIEES_LINK =
  'https://www.demarches-simplifiees.fr/commencer/activer-mon-compte-pass-culture'

const ActivationOnlineButton = () => (
  <div className="mb36">
    <div className="mb36">
      <a
        target="_blank"
        rel="noopener noreferrer"
        id="activation-online-button"
        href={DEMARCHE_SIMPLIFIEES_LINK}
        className="is-block text-center button is-rounded py7 no-background"
      >
        <span className="fs18 is-white-text is-bold">
          Activer votre pass en ligne
        </span>
      </a>
    </div>
    <div className="text-center">
      <span className="is-italic is-medium fs20">--&nbsp;ou&nbsp;--</span>
    </div>
  </div>
)

export default ActivationOnlineButton
