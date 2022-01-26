import React, { forwardRef, useCallback, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import CanvasTools from './canvas'

export type ImageEditorProps = {
  image: string | File
  canvasHeight: number
  canvasWidth: number
  cropBorderColor: string
  cropBorderHeight: number
  cropBorderWidth: number
  children?: never
}

const ImageEditor = forwardRef<AvatarEditor, ImageEditorProps>(
  (
    {
      image,
      canvasHeight,
      canvasWidth,
      cropBorderColor,
      cropBorderHeight,
      cropBorderWidth,
    },
    ref
  ) => {
    const [scale, setScale] = useState(1)

    const drawCropBorder = useCallback(() => {
      const canvas = document.querySelector('canvas')
      const ctx = canvas?.getContext('2d')
      const canvasTools = new CanvasTools(ctx)
      canvasTools.drawArea({
        width: 0,
        color: cropBorderColor,
        coordinates: [
          cropBorderWidth,
          cropBorderHeight,
          canvasWidth,
          canvasHeight,
        ],
      })
    }, [
      cropBorderColor,
      cropBorderWidth,
      cropBorderHeight,
      canvasWidth,
      canvasHeight,
    ])
    const onScaleChange = useCallback(event => {
      setScale(event.target.value)
    }, [])

    return (
      <>
        <div className="tnr-canvas">
          <AvatarEditor
            border={[cropBorderWidth, cropBorderHeight]}
            color={[0, 0, 0, 0.4]}
            height={canvasHeight}
            image={image}
            onImageChange={drawCropBorder}
            onImageReady={drawCropBorder}
            onMouseMove={drawCropBorder}
            onMouseUp={drawCropBorder}
            ref={ref}
            scale={Number(scale)}
            width={canvasWidth}
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
)
ImageEditor.displayName = 'ImageEditor'

export default ImageEditor
