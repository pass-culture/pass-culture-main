import React from 'react'
import FormFooter from '../../forms/FormFooter'
import Icon from '../../layout/Icon/Icon'
import PropTypes from 'prop-types'

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
        {'votre pass Culture'}
      </div>
      <div className="bp-content">
        {'Vous avez 18 ans et vivez dans un\n'}
        <a
          href="https://pass.culture.fr/#jeune"
          rel="noopener noreferrer"
          target="_blank"
        >
          {'département éligible ?'}
        </a>
      </div>
      <div className="bp-content">
        {'Bénéficiez de 500 € afin de\n'}
        {'renforcer vos pratiques\n'}
        {"culturelles et d'en découvrir\n"}
        {'de nouvelles !'}
      </div>
    </main>
    <FormFooter
      externalLink={{
        id: 'sign-up-link',
        label: 'Créer un compte',
        title: 'Créer un compte (nouvelle fenêtre)',
        url: 'https://www.demarches-simplifiees.fr/commencer/inscription-pass-culture',
        tracker: trackSignup,
      }}
      submit={{
        id: 'sign-in-link',
        label: "J'ai un compte",
        url: '/connexion',
      }}
    />
  </div>
)

BetaPage.propTypes = {
  trackSignup: PropTypes.func.isRequired,
}

export default BetaPage
