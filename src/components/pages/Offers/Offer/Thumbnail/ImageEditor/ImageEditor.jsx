import PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import CanvasTools from 'utils/canvas'

const ImageEditor = ({ setCroppingRect, setEditedThumbnail, setStep, step, thumbnail, url }) => {
  const image = url !== '' ? url : thumbnail
  const [scale, setScale] = useState(1)
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

  const onScaleChange = useCallback(event => {
    setScale(event.target.value)
  }, [])

  const drawCropBorder = useCallback(ctx => {
    const canvas = new CanvasTools(ctx)

    canvas.drawArea({
      width: 0,
      color: CROP_BORDER_COLOR,
      coordinates: [CROP_BORDER_WIDTH, CROP_BORDER_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT],
    })
  }, [])

  return (
    <>
      <div className="tnd-subtitle">
        {'Recadrer votre image'}
      </div>
      <div className="tnr-canvas">
        <AvatarEditor
          border={[CROP_BORDER_WIDTH, CROP_BORDER_HEIGHT]}
          color={[0, 0, 0, 0.4]}
          height={CANVAS_HEIGHT}
          image={image}
          onImageChange={drawCropBorder}
          ref={editorRef}
          scale={Number(scale)}
          width={CANVAS_WIDTH}
        />
      </div>
      <label htmlFor="scale">
        {'Zoom'}
      </label>
      <div className="tnr-scale">
        <span>
          {'min'}
        </span>
        <input
          id="scale"
          max="4"
          min="1"
          onChange={onScaleChange}
          step="0.01"
          type="range"
          value={scale}
        />
        <span>
          {'max'}
        </span>
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
          onClick={nextStep}
          title="Suivant"
          type="button"
        >
          {'Prévisualiser'}
        </button>
      </div>
    </>
  )
}

ImageEditor.defaultProps = {
  thumbnail: {},
  url: '',
}

ImageEditor.propTypes = {
  setCroppingRect: PropTypes.func.isRequired,
  setEditedThumbnail: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
  thumbnail: PropTypes.shape(),
  url: PropTypes.string,
}

export default ImageEditor
