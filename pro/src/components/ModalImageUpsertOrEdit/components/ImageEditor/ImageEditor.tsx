import {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import AvatarEditor, {
  type AvatarEditorRef,
  type Position,
} from 'react-avatar-editor'
import { useDebouncedCallback } from 'use-debounce'

import { Slider } from '@/ui-kit/form/Slider/Slider'

import { CanvasTools } from './canvas'
import style from './ImageEditor.module.scss'

const CANVAS_MOBILE_BREAKPOINT = 600
// The library default (1 px) is too small to change the announced percentages
const KEYBOARD_STEP_IN_PX = 5
// Lets the user chain key presses / drag before the new state is announced
const EDITOR_STATE_ANNOUNCEMENT_DELAY_IN_MS = 500

type CroppingRect = ReturnType<AvatarEditorRef['getCroppingRect']>

function clamp(input: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, input))
}

const toPercentage = (ratio: number) => Math.round(clamp(ratio, 0, 1) * 100)

function getEditorStateDescription(
  zoomPercentage: number,
  { x, y, width, height }: CroppingRect
): string {
  return (
    `Zoom : ${zoomPercentage} %. ` +
    `Zone cadrée : de ${toPercentage(x)} à ${toPercentage(x + width)} % de la largeur ` +
    `et de ${toPercentage(y)} à ${toPercentage(y + height)} % de la hauteur de l’image.`
  )
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
  onImageError?: () => void
}

export const ImageEditor = forwardRef<AvatarEditorRef, ImageEditorProps>(
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
      onImageError,
    },
    ref
  ) => {
    const imageDisableDescriptionId = useId()
    const editorStateId = useId()
    const keyboardInstructionsId = useId()
    const zoomSliderId = useId()
    const editorRef = useRef<AvatarEditorRef>(null)
    const [position, setPosition] = useState<Position>(initialPosition)
    const [windowWidth, setWindowWidth] = useState(window.innerWidth)
    const [isImageReady, setIsImageReady] = useState(false)
    const [editorStateDescription, setEditorStateDescription] = useState('')

    const [scale, setScale] = useState<number>(initialScale)
    const zoomPercentage = Math.round(scale * 100)

    // Keeps a local access to the editor while still exposing it to the parent
    useImperativeHandle(ref, () => {
      const getEditor = () => {
        if (!editorRef.current) {
          throw new Error('The image editor is not mounted')
        }
        return editorRef.current
      }

      return {
        getImage: () => getEditor().getImage(),
        getImageScaledToCanvas: () => getEditor().getImageScaledToCanvas(),
        getCroppingRect: () => getEditor().getCroppingRect(),
      }
    }, [])

    // Read once the editor has repainted, so that the cropping rect is up to date
    // biome-ignore lint/correctness/useExhaustiveDependencies: position is not read but moves the cropping rect
    useEffect(() => {
      if (!isImageReady) {
        return
      }

      const timeoutId = setTimeout(() => {
        const croppingRect = editorRef.current?.getCroppingRect()
        if (croppingRect) {
          setEditorStateDescription(
            getEditorStateDescription(zoomPercentage, croppingRect)
          )
        }
      }, EDITOR_STATE_ANNOUNCEMENT_DELAY_IN_MS)

      return () => clearTimeout(timeoutId)
    }, [isImageReady, zoomPercentage, position])

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
    // Derived from the height so that the crop area always keeps the same aspect ratio
    const responsiveCanvasWidth =
      responsiveCanvasHeight * (canvasWidth / canvasHeight)
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

    // Debounce onChangeDone to avoid too many calls
    const debouncedOnChangeDone = useDebouncedCallback(
      () => onChangeDone?.(),
      100
    )

    // Called on mouse / touch drag and on keyboard arrows
    const onPositionChange = useCallback(
      (position: Position) => {
        setPosition(position)
        debouncedOnChangeDone()
      },
      [debouncedOnChangeDone]
    )

    const isScaleDisabled = maxScale <= 1
    // Force a minimum zoom level of 2x when zoom is available (prevents the user from zooming too little)
    // If zoom enabled AND maxScale < 2, use 2; otherwise use maxScale (e.g., 1.5 → 2, 3 → 3)
    const effectiveMaxScale = !isScaleDisabled && maxScale < 2 ? 2 : maxScale

    // Called on keyboard "+" / "-" and on pinch-to-zoom
    const onRequestScaleChange = (requestedScale: number) => {
      if (isScaleDisabled) {
        return
      }
      setScale(clamp(requestedScale, 1, effectiveMaxScale))
      debouncedOnChangeDone()
    }

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
      <div
        className={style['image-editor']}
        // react-avatar-editor hardcodes english ARIA attributes on the canvas
        ref={(el) => {
          const canvas = el?.querySelector('canvas')
          canvas?.setAttribute(
            'aria-label',
            "Editeur de cadrage et de zoom de l'image"
          )
          canvas?.setAttribute('aria-roledescription', 'éditeur d’image')
          canvas?.setAttribute(
            'aria-describedby',
            `${editorStateId} ${keyboardInstructionsId}`
          )
        }}
      >
        <AvatarEditor
          color={[0, 0, 0, 0.2]}
          crossOrigin="anonymous"
          image={image}
          keyboardStep={KEYBOARD_STEP_IN_PX}
          onLoadFailure={onImageError}
          onImageChange={drawCropBorder}
          onImageReady={() => {
            onImagePainted?.()
            drawCropBorder()
            setIsImageReady(true)
          }}
          onPositionChange={onPositionChange}
          onRequestScaleChange={onRequestScaleChange}
          position={position}
          ref={editorRef}
          scale={scale}
          width={responsiveCanvasWidth}
          height={responsiveCanvasHeight}
          border={[responsiveCropBorderWidth, responsiveCropBorderHeight]}
        />
        <output
          id={editorStateId}
          className={style['image-editor-visually-hidden']}
        >
          {editorStateDescription}
        </output>
        <span
          id={keyboardInstructionsId}
          className={style['image-editor-visually-hidden']}
        >
          {isScaleDisabled
            ? 'Utilisez les flèches du clavier pour déplacer l’image.'
            : 'Utilisez les flèches du clavier pour déplacer l’image et les touches + et - pour zoomer.'}
        </span>
        <label className={style['image-editor-label']} htmlFor={zoomSliderId}>
          Zoom : {zoomPercentage} %
        </label>
        <div className={style['image-editor-scale']}>
          <span className={style['image-editor-scale-label']}>min</span>
          <div className={style['image-editor-scale-input']}>
            <Slider
              id={zoomSliderId}
              name="scale"
              step={0.01}
              max={!isScaleDisabled ? effectiveMaxScale.toFixed(2) : 1}
              min={1}
              displayMinMaxValues={false}
              value={scale}
              onChange={(e) => {
                setScale(Number(e.target.value))
                debouncedOnChangeDone()
              }}
              disabled={isScaleDisabled}
              aria-describedby={imageDisableDescriptionId}
              aria-valuetext={`Zoom ${zoomPercentage} %`}
              label="Niveau de zoom de l'image"
              hideLabel
            />
          </div>
          <span className={style['image-editor-scale-label']}>max</span>
        </div>
        {isScaleDisabled && (
          <span
            id={imageDisableDescriptionId}
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
