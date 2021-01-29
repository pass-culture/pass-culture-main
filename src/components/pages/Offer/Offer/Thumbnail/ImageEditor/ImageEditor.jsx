import PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offer/Offer/Thumbnail/_constants'
import CanvasTools from 'utils/canvas'

const ImageEditor = ({ setEditedThumbnail, setStep, thumbnail, url }) => {
  const image = url !== '' ? url : thumbnail
  const [scale, setScale] = useState(1)
  const editorRef = useRef({})

  const previousStep = useCallback(() => {
    setStep(2)
  }, [setStep])

  const nextStep = useCallback(() => {
    if (editorRef.current) {
      const canvas = editorRef.current.getImage()
      setEditedThumbnail(canvas.toDataURL())
      setStep(4)
    }
  }, [setEditedThumbnail, setStep])

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
  setEditedThumbnail: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
  thumbnail: PropTypes.shape(),
  url: PropTypes.string,
}

export default ImageEditor
