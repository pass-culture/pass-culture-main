/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback, useRef } from 'react'

import ImageEditor from 'components/pages/Offers/Offer/Thumbnail/ImageEditor/ImageEditor'

const ImageEditorWrapper = ({
  setCroppingRect,
  setEditedThumbnail,
  setStep,
  step,
  thumbnail,
}) => {
  const editorRef = useRef({})

  const previousStep = useCallback(() => {
    setStep(step - 1)
  }, [setStep, step])

  const nextStep = useCallback(() => {
    if (editorRef.current) {
      const canvas = editorRef.current.getImage()
      const croppingRect = editorRef.current.getCroppingRect()
      setCroppingRect(croppingRect)
      setEditedThumbnail(canvas.toDataURL())
      setStep(step + 1)
    }
  }, [setCroppingRect, setEditedThumbnail, setStep, step])

  return (
    <>
      <div className="tnd-subtitle">Recadrer votre image</div>
      <ImageEditor image={thumbnail} ref={editorRef} />
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
          Prévisualiser
        </button>
      </div>
    </>
  )
}

ImageEditorWrapper.defaultProps = {
  thumbnail: {},
}

ImageEditorWrapper.propTypes = {
  setCroppingRect: PropTypes.func.isRequired,
  setEditedThumbnail: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
  thumbnail: PropTypes.shape(),
}

export default ImageEditorWrapper
