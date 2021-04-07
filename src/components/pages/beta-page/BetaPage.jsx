import PropTypes from 'prop-types'
import React, { useEffect, useRef } from 'react'

import FormFooter from '../../forms/FormFooter'
import Icon from '../../layout/Icon/Icon'

const BetaPage = ({ trackSignup, isNewBookingLimitsActived, wholeFranceOpening }) => {
  const appTitle = useRef(null)

  useEffect(() => {
    appTitle.current.focus()
  }, [])

  return (
    <div className="beta-page">
      <Icon
        alt=""
        className="bp-logo"
        svg="circle"
      />
      <main className="bp-main">
        <div
          className="bp-title"
          ref={appTitle}
          // eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex
          tabIndex={0}
        >
          {'Bienvenue dans\n'}
          {'ton pass Culture'}
        </div>
        <div className="bp-content">
          {'Tu as 18 ans'}
          {!wholeFranceOpening && (
            <span>
              {' et tu vis dans un '}
              <a
                href="https://pass.culture.fr/le-dispositif/#dispoexpe"
                rel="noopener noreferrer"
                target="_blank"
              >
                {'département éligible'}
              </a>
            </span>
          )}
          {' ?'}
        </div>
        <div className="bp-content">
          {`Bénéficie de ${isNewBookingLimitsActived ? 300 : 500} € afin de\n`}
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
            label: 'Me connecter',
            url: '/connexion',
          },
        ]}
      />
    </div>
  )
}

BetaPage.propTypes = {
  isNewBookingLimitsActived: PropTypes.bool.isRequired,
  trackSignup: PropTypes.func.isRequired,
  wholeFranceOpening: PropTypes.bool.isRequired,
}

export default BetaPage
