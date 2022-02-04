import PropTypes from 'prop-types'
import React, { forwardRef, useCallback, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import CanvasTools from 'components/pages/Offers/Offer/Thumbnail/ImageEditor/canvas'

export const ImageEditor = ({ image }, ref) => {
  const [scale, setScale] = useState(1)

  const drawCropBorder = useCallback(() => {
    const canvas = document.querySelector('canvas')
    const ctx = canvas.getContext('2d')
    const canvasTools = new CanvasTools(ctx)
    canvasTools.drawArea({
      width: 0,
      color: CROP_BORDER_COLOR,
      coordinates: [
        CROP_BORDER_WIDTH,
        CROP_BORDER_HEIGHT,
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
      ],
    })
  }, [])
  const onScaleChange = useCallback(event => {
    setScale(event.target.value)
  }, [])

  return (
    <>
      <div className="tnr-canvas">
        <AvatarEditor
          border={[CROP_BORDER_WIDTH, CROP_BORDER_HEIGHT]}
          color={[0, 0, 0, 0.4]}
          height={CANVAS_HEIGHT}
          image={image}
          onImageChange={drawCropBorder}
          onImageReady={drawCropBorder}
          onMouseMove={drawCropBorder}
          onMouseUp={drawCropBorder}
          ref={ref}
          scale={Number(scale)}
          width={CANVAS_WIDTH}
        />
      </div>
      <label htmlFor="scale">Zoom</label>
      <div className="tnr-scale">
        <span>min</span>
        <input
          id="scale"
          max="4"
          min="1"
          onChange={onScaleChange}
          step="0.01"
          type="range"
          value={scale}
        />
        <span>max</span>
      </div>
    </>
  )
}
export default forwardRef(ImageEditor)

ImageEditor.propTypes = {
  image: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(File)])
    .isRequired,
}
