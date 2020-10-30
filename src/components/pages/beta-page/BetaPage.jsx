import PropTypes from 'prop-types'
import React from 'react'

import FormFooter from '../../forms/FormFooter'
import Icon from '../../layout/Icon/Icon'

const BetaPage = ({ trackSignup }) => (
  <div className="beta-page">
    <Icon
      alt=""
      className="bp-logo"
      svg="circle"
    />
    <main className="bp-main">
      <div className="bp-title">
        {'Bienvenue dans\n'}
        {'ton pass Culture'}
      </div>
      <div className="bp-content">
        {'Tu as 18 ans et tu vis dans un\n'}
        <a
          href="https://pass.culture.fr/le-dispositif/#dispoexpe"
          rel="noopener noreferrer"
          target="_blank"
        >
          {'département éligible ?'}
        </a>
      </div>
      <div className="bp-content">
        {'Bénéficie de 500 € afin de\n'}
        {'renforcer tes pratiques\n'}
        {"culturelles et d'en découvrir\n"}
        {'de nouvelles !'}
      </div>
    </main>
    <FormFooter
      items={[
        {
          id: 'sign-up-link',
          label: 'Créer un compte',
          url: '/verification-eligibilite',
          tracker: trackSignup,
        },
        {
          id: 'sign-in-link',
          label: "J'ai un compte",
          url: '/connexion',
        },
      ]}
    />
  </div>
)

BetaPage.propTypes = {
  trackSignup: PropTypes.func.isRequired,
}

export default BetaPage
