import { forwardRef, useCallback, useEffect, useState } from 'react'
import AvatarEditor, { Position } from 'react-avatar-editor'
import { useDebouncedCallback } from 'use-debounce'

import { Slider } from 'ui-kit/form/Slider/Slider'

import { CanvasTools } from './canvas'
import style from './ImageEditor.module.scss'

const CANVAS_MOBILE_BREAKPOINT = 600

function clamp(input: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, input))
}

export function map(
  current: number,
  in_min: number,
  in_max: number,
  out_min: number,
  out_max: number
): number {
  const mapped: number =
    ((current - in_min) * (out_max - out_min)) / (in_max - in_min) + out_min
  return clamp(mapped, out_min, out_max)
}

interface ImageEditorConfig {
  canvasHeight: number
  canvasWidth: number
  cropBorderHeight: number
  cropBorderWidth: number
  maxScale: number
}

interface ImageEditorProps extends ImageEditorConfig {
  image: File
  initialPosition?: Position
  initialScale?: number
  children?: never
  onChangeDone?: () => void
  onImagePainted?: () => void
}

export const ImageEditor = forwardRef<AvatarEditor, ImageEditorProps>(
  (
    {
      image,
      canvasHeight,
      canvasWidth,
      cropBorderHeight,
      cropBorderWidth,
      initialPosition = { x: 0.5, y: 0.5 },
      maxScale = 4,
      initialScale = 1,
      onChangeDone,
      onImagePainted,
    },
    ref
  ) => {
    const [position, setPosition] = useState<Position>(initialPosition)
    const [windowWidth, setWindowWidth] = useState(window.innerWidth)

    const [scale, setScale] = useState<number>(initialScale)

    useEffect(() => {
      const handleResize = () => {
        setWindowWidth(window.innerWidth)
      }

      window.addEventListener('resize', handleResize)

      return () => {
        window.removeEventListener('resize', handleResize)
      }
    }, [])

    // The modal is too big for mobile phone.
    const responsiveCanvasHeight = map(
      windowWidth,
      0,
      CANVAS_MOBILE_BREAKPOINT,
      100,
      canvasHeight
    )
    const responsiveCanvasWidth = map(
      windowWidth,
      0,
      CANVAS_MOBILE_BREAKPOINT,
      100,
      canvasWidth
    )
    const responsiveCropBorderWidth = map(
      windowWidth,
      0,
      CANVAS_MOBILE_BREAKPOINT,
      0,
      cropBorderWidth
    )
    const responsiveCropBorderHeight = map(
      windowWidth,
      0,
      CANVAS_MOBILE_BREAKPOINT,
      0,
      cropBorderHeight
    )

    /* istanbul ignore next: DEBT, TO FIX */
    const onPositionChange = useCallback((position: Position) => {
      setPosition(position)
    }, [])

    // Debounce onChangeDone to avoid too many calls
    const debouncedOnSearch = useDebouncedCallback(() => onChangeDone?.(), 100)

    const isScaleDisabled = maxScale <= 1

    const drawCropBorder = () => {
      const canvas = document.querySelector('canvas')
      const ctx = canvas?.getContext('2d')
      if (!ctx) {
        return
      }

      const canvasTools = new CanvasTools(ctx)
      canvasTools.drawArea({
        width: 0,
        color: '#FFF',
        coordinates: [
          responsiveCropBorderWidth,
          responsiveCropBorderHeight,
          responsiveCanvasWidth,
          responsiveCanvasHeight,
        ],
      })
    }

    return (
      <div className={style['image-editor']}>
        <AvatarEditor
          color={[0, 0, 0, 0.2]}
          crossOrigin="anonymous"
          image={image}
          onImageChange={drawCropBorder}
          onImageReady={() => {
            onImagePainted?.()
            drawCropBorder()
          }}
          onMouseUp={onChangeDone}
          onPositionChange={onPositionChange}
          position={position}
          ref={ref}
          scale={scale}
          width={responsiveCanvasWidth}
          height={responsiveCanvasHeight}
          border={[responsiveCropBorderWidth, responsiveCropBorderHeight]}
          aria-label="Editeur d'image"
        />
        <label className={style['image-editor-label']} htmlFor="scale">
          Zoom
        </label>
        <div className={style['image-editor-scale']}>
          <span className={style['image-editor-scale-label']}>min</span>
          <div className={style['image-editor-scale-input']}>
            <Slider
              name="scale"
              step={0.01}
              max={!isScaleDisabled ? maxScale.toFixed(2) : 1}
              min={1}
              displayMinMaxValues={false}
              value={scale}
              onChange={(e) => {
                setScale(Number(e.target.value))
                debouncedOnSearch()
              }}
              disabled={isScaleDisabled}
              aria-describedby="image-editor-scale-disabled"
              hideLabel
            />
          </div>
          <span className={style['image-editor-scale-label']}>max</span>
        </div>
        {isScaleDisabled && (
          <span
            id="image-editor-scale-disabled"
            className={style['image-editor-scale-disabled']}
          >
            L’image est trop petite pour utiliser le zoom.
          </span>
        )}
      </div>
    )
  }
)
ImageEditor.displayName = 'ImageEditor'
