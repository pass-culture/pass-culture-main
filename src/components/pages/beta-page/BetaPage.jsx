import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef } from 'react'
import Icon from '../../layout/Icon/Icon'
import SmartBanner from 'react-smartbanner'
import { Link } from 'react-router-dom'

const BetaPage = ({ isNewBookingLimitsActived }) => {
  const appTitle = useRef(null)
  const handleRedirectionToApp = useCallback(
    () =>
      window.open(
        'https://passcultureapp.page.link/?link=https://passculture.app/default&apn=app.passculture.webapp&isi=1557887412&ibi=app.passculture&efr=1&ofl=https://pass.culture.fr/nosapplications'
      ),
    []
  )

  useEffect(() => {
    appTitle.current.focus()
  }, [])

  return (
    <div className="beta-page">
      <SmartBanner
        button="Voir"
        daysHidden={1}
        position="top"
        price={{ ios: 'GRATUIT', android: 'GRATUIT' }}
        storeText={{ ios: "Sur l'App Store", android: 'Sur Google Play' }}
        title="pass Culture"
      />
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
        <h2 className="lf-subtitle">
          {'Tu as 18 ans ?'}
        </h2>
        <div className="bp-content">
          {`Bénéficie de ${isNewBookingLimitsActived ? 300 : 500} € afin de\n`}
          {'renforcer tes pratiques\n'}
          {"culturelles et d'en découvrir\n"}
          {'de nouvelles !'}
        </div>
        <div className="bp-content">
          {`Si tu veux profiter des dernières \n`}
          {"fonctionnalités, télécharge l'application \n"}
          {'depuis les stores.'}
        </div>
        <div className="buttons-container">
          <Link
            className="sign-in-button"
            to="/connexion"
            type="button"
          >
            {'Se connecter'}
          </Link>
          <button
            className="download-app-button"
            onClick={handleRedirectionToApp}
            type="button"
          >
            <Icon
              alt="Lien vers l'app"
              class="external-link-icon"
              svg="external-link-site"
            />
            <span className="download-app">
              {"Télécharger l'application"}
            </span>
          </button>
        </div>
      </main>
    </div>
  )
}

BetaPage.propTypes = {
  isNewBookingLimitsActived: PropTypes.bool.isRequired,
}

export default BetaPage
