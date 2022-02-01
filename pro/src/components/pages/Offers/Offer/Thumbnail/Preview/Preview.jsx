/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { ImagePreview } from 'new_components/ImagePreview/ImagePreview'

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
      <ImagePreview preview={preview} />
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
