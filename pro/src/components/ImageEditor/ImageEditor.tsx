import { useFormikContext } from 'formik'
import React, { forwardRef, useCallback, useState } from 'react'
import AvatarEditor, { Position } from 'react-avatar-editor'

import { ImageEditorFormValues } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageCrop/ModalImageCrop'
import Slider from 'ui-kit/form/Slider/Slider'

import CanvasTools from './canvas'
import style from './ImageEditor.module.scss'

export interface ImageEditorConfig {
  canvasHeight: number
  canvasWidth: number
  cropBorderColor: string
  cropBorderHeight: number
  cropBorderWidth: number
  maxScale: number
}

export interface ImageEditorProps extends ImageEditorConfig {
  image: File
  initialPosition?: Position
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
      initialPosition = { x: 0.5, y: 0.5 },
      maxScale = 4,
    },
    ref
  ) => {
    const [position, setPosition] = useState<Position>(initialPosition)
    const formik = useFormikContext<ImageEditorFormValues>()
    const drawCropBorder = useCallback(() => {
      const canvas = document.querySelector('canvas')
      const ctx = canvas?.getContext('2d')

      if (!ctx) {
        return
      }
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

    /* istanbul ignore next: DEBT, TO FIX */
    const onPositionChange = useCallback((position: Position) => {
      setPosition(position)
    }, [])

    return (
      <div className={style['image-editor']}>
        <AvatarEditor
          border={[cropBorderWidth, cropBorderHeight]}
          color={[0, 0, 0, 0.4]}
          crossOrigin="anonymous"
          height={canvasHeight}
          image={image}
          onImageChange={drawCropBorder}
          onImageReady={drawCropBorder}
          onMouseMove={drawCropBorder}
          onMouseUp={drawCropBorder}
          onPositionChange={onPositionChange}
          position={position}
          ref={ref}
          scale={Number(formik.values.scale)}
          width={canvasWidth}
        />
        <label className={style['image-editor-label']} htmlFor="scale">
          Zoom
        </label>
        <label className={style['image-editor-scale']} htmlFor="scale">
          <span className={style['image-editor-scale-label']}>min</span>
          <span className={style['image-editor-scale-input']}>
            <Slider
              fieldName="scale"
              step={0.01}
              max={maxScale > 1 ? maxScale.toFixed(2) : 1}
              min={1}
              displayMinMaxValues={false}
            />
          </span>
          <span className={style['image-editor-scale-label']}>max</span>
        </label>
      </div>
    )
  }
)
ImageEditor.displayName = 'ImageEditor'

export default ImageEditor
