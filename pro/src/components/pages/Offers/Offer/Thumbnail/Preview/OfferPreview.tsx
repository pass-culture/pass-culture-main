/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import React, { FunctionComponent, useCallback } from 'react'

import { OfferPreviews } from './OfferPreviews/OfferPreviews'

interface Props {
  preview: string
  setStep: (step: number) => void
  step: number
}

const OfferPreview: FunctionComponent<Props> = ({ preview, setStep, step }) => {
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
      <OfferPreviews previewImageURI={preview} />
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

export default OfferPreview
