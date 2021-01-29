import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import homeShell from 'components/pages/Offer/Offer/Thumbnail/assets/home-shell.png'
import { ReactComponent as MobileShell } from 'components/pages/Offer/Offer/Thumbnail/assets/mobile-shell.svg'
import offerShell from 'components/pages/Offer/Offer/Thumbnail/assets/offer-shell.png'

const Preview = ({ preview, setStep }) => {
  const previousStep = useCallback(() => {
    setStep(3)
  }, [setStep])

  return (
    <>
      <div className="tnd-subtitle">
        {'Prévisualisation de votre image dans l’application pass Culture'}
      </div>
      <div className="tnp-previews">
        <div className="tnp-previews-wrapper">
          <MobileShell />
          <img
            alt=""
            className="tnp-shell"
            src={homeShell}
          />
          <img
            alt=""
            className="tnp-home-preview"
            height="163"
            src={preview}
            width="108"
          />
          <div>
            {'Page d’accueil'}
          </div>
        </div>
        <div className="tnp-previews-wrapper">
          <MobileShell />
          <img
            alt=""
            className="tnp-shell"
            src={offerShell}
          />
          <img
            alt=""
            className="tnp-offer-preview"
            height="175"
            src={preview}
            width="116"
          />
          <div>
            {'Détail de l’offre'}
          </div>
        </div>
      </div>
      <div className="tnd-actions">
        <button
          className="secondary-button"
          onClick={previousStep}
          title="Retour"
          type="button"
        >
          {'Retour'}
        </button>
        <button
          className="primary-button"
          title="Suivant"
          type="button"
        >
          {'Valider'}
        </button>
      </div>
    </>
  )
}

Preview.propTypes = {
  preview: PropTypes.string.isRequired,
  setStep: PropTypes.func.isRequired,
}

export default Preview
