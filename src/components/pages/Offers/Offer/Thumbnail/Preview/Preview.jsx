/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import homeShell from 'components/pages/Offers/Offer/Thumbnail/assets/home-shell.png'
import { ReactComponent as MobileShell } from 'components/pages/Offers/Offer/Thumbnail/assets/mobile-shell.svg'
import offerShell from 'components/pages/Offers/Offer/Thumbnail/assets/offer-shell.png'

const Preview = ({ preview, setStep, step }) => {
  const previousStep = useCallback(() => {
    setStep(step - 1)
  }, [setStep, step])

  const nextStep = useCallback(() => {
    setStep(step + 1)
  }, [setStep, step])

  return (
    <>
      <div className="tnd-subtitle">
        Prévisualisation de votre image dans l’application pass Culture
      </div>
      <div className="tnp-previews">
        <div className="tnp-previews-wrapper">
          <MobileShell />
          <img
            alt=""
            className="tnp-shell"
            height="515"
            src={homeShell}
          />
          <img
            alt=""
            className="tnp-home-preview"
            height="228"
            src={preview}
          />
          <div>
            Page d’accueil
          </div>
        </div>
        <div className="tnp-previews-wrapper">
          <MobileShell />
          <img
            alt=""
            className="tnp-blur-offer-preview"
            height="435"
            src={preview}
          />
          <img
            alt=""
            className="tnp-shell right"
            height="280"
            src={offerShell}
          />
          <img
            alt=""
            className="tnp-offer-preview"
            height="247"
            src={preview}
          />
          <div>
            Détail de l’offre
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
          Retour
        </button>
        <button
          className="primary-button"
          onClick={nextStep}
          title="Suivant"
          type="button"
        >
          Valider
        </button>
      </div>
    </>
  )
}

Preview.propTypes = {
  preview: PropTypes.string.isRequired,
  setStep: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default Preview
