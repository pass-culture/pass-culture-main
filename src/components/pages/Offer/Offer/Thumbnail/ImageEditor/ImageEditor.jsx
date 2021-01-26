import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offer/Offer/Thumbnail/_constants'
import CanvasTools from 'utils/canvas'

const ImageEditor = ({ setStep, thumbnail }) => {
  const [scale, setScale] = useState(1)

  const previousStep = useCallback(() => {
    setStep(2)
  }, [setStep])

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
          image={thumbnail}
          onImageChange={drawCropBorder}
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
          title="Suivant"
          type="button"
        >
          {'Prévisualiser'}
        </button>
      </div>
    </>
  )
}

ImageEditor.propTypes = {
  setStep: PropTypes.func.isRequired,
  thumbnail: PropTypes.shape().isRequired,
}

export default ImageEditor
