import Slider from '@mui/material/Slider'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { styled } from '@mui/material/styles'
import React, { forwardRef, useCallback, useState } from 'react'
import AvatarEditor from 'react-avatar-editor'

import CanvasTools from './canvas'
import style from './ImageEditor.module.scss'

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
    const theme = createTheme({
      palette: {
        primary: {
          main: '#eb0055',
          dark: '#eb0055',
          light: '#eb0055',
        },
      },
    })

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
          ref={ref}
          scale={Number(scale)}
          width={canvasWidth}
        />
        <label className={style['image-editor-label']} htmlFor="scale">
          Zoom
        </label>
        <label className={style['image-editor-scale']} htmlFor="scale">
          <span className={style['image-editor-scale-label']}>min</span>
          <span className={style['image-editor-scale-input']}>
            <ThemeProvider theme={theme}>
              <CustomSlider
                max={4}
                min={1}
                onChange={onScaleChange}
                step={0.01}
                value={scale}
              />
            </ThemeProvider>
          </span>
          <span className={style['image-editor-scale-label']}>max</span>
        </label>
      </div>
    )
  }
)
const CustomSlider = styled(Slider)(() => ({
  '& .MuiSlider-thumb': {
    height: 16,
    width: 16,
  },
}))
ImageEditor.displayName = 'ImageEditor'

export default ImageEditor
