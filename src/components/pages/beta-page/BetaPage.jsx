import React, { useCallback, useEffect, useRef } from 'react'
import Icon from '../../layout/Icon/Icon'
import SmartBanner from 'react-smartbanner'
import { Link } from 'react-router-dom'
import {
  APP_NATIVE_DYNAMIC_LINK,
  ANDROID_APP_ID,
  IOS_APP_STORE_ID,
  IOS_APP_ID,
  UNIVERSAL_LINK,
} from '../../../utils/config'

const BetaPage = () => {
  const appTitle = useRef(null)
  const handleRedirectionToApp = useCallback(
    () =>
      window.open(
        `${APP_NATIVE_DYNAMIC_LINK}/?link=https://${UNIVERSAL_LINK}/default&apn=${ANDROID_APP_ID}&isi=${IOS_APP_STORE_ID}&ibi=${IOS_APP_ID}&efr=1&ofl=https://pass.culture.fr/nosapplications`
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
          {'Bienvenue sur\n'}
          {'le pass Culture,'}
        </div>
        <div className="bp-content">
          {`l'application pour découvrir les activités et\n`}
          {'sorties culturelles proches de chez toi et\n'}
          {'partout en France.'}
        </div>
        <div className="bp-content">
          {`Pour profiter au mieux des fonctionnalités de\n`}
          {"l'application, télécharge-la depuis les stores."}
        </div>
        <div className="bp-content">
          {`Tu as déjà un compte ?\n`}
          {'Connecte-toi vite pour réserver et profiter de\n'}
          {'toutes les offres disponibles !'}
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
            <svg
              height="24"
              viewBox="0 0 24 24"
              width="24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M11.614 8.25c.288.004.431.155.431.455 0 .299-.143.45-.431.454h-4.75v8.182h7.772v-5c0-.303.144-.455.432-.455.288 0 .432.152.432.455v5.454a.444.444 0 01-.432.455H6.432A.444.444 0 016 17.795v-9.09c0-.251.193-.455.432-.455h5.182zm2.979-2.999l.08.002 2.86.343a.45.45 0 01.386.405l.328 2.993a.456.456 0 01-.386.51.446.446 0 01-.486-.405l-.23-2.088-5.627 5.89a.423.423 0 01-.62 0 .474.474 0 010-.65l5.595-5.855-1.92-.23a.452.452 0 01-.389-.426l.002-.083a.444.444 0 01.486-.404z"
                fill="#FFF"
                fillRule="evenodd"
              />
            </svg>
            <span className="download-app">
              {"Télécharger l'application"}
            </span>
          </button>
        </div>
      </main>
    </div>
  )
}

export default BetaPage
