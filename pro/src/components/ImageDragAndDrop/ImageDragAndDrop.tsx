import cn from 'classnames'
import { type ForwardedRef, forwardRef, useId, useState } from 'react'
import { useDropzone } from 'react-dropzone'

import fullValidateIcon from '@/icons/full-validate.svg'
import strokePicture from '@/icons/stroke-picture.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import {
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE,
  UPLOAD_IMAGE_MAX_RESOLUTION,
} from './constants'
import { getImageDimensions } from './getImageDimensions'
import { ImageConstraintCheck } from './ImageConstraintCheck'
import styles from './ImageDragAndDrop.module.scss'

interface ImageDragAndDropProps {
  /**
   * Class name for the drag and drop area.
   */
  className?: string
  /**
   * Callback triggered when the user clicks on the drag and drop area.
   */
  onClick?: () => void
  /**
   * Callback triggered when a file is dropped or selected.
   */
  onDropOrSelected?: (file: File) => void
  /**
   * Callback triggered when an error occurs, e.g. wrong file type or size.
   */
  onError?: (err?: string[]) => void
  /**
   * Either if the drag and drop component is disabled or not.
   */
  disabled?: boolean
  /**
   * Min size constraints for the image.
   * Optional.
   */
  minSizes?: {
    width?: number
    height?: number
  }
}

export const ImageDragAndDrop = forwardRef(
  (
    {
      className,
      onClick,
      onDropOrSelected,
      onError,
      disabled,
      minSizes,
    }: ImageDragAndDropProps,
    dragAndDropInputRef: ForwardedRef<HTMLInputElement>
  ) => {
    const [hasInput, setHasInput] = useState(false)
    const [isDraggedOver, setIsDraggedOver] = useState(false)
    const [isHovered, setIsHovered] = useState(false)
    const [isFocused, setIsFocused] = useState(false)
    const [customErrors, setCustomErrors] = useState<string[]>([])

    const handleDrop = async (files: File[]) => {
      setHasInput(true)
      setCustomErrors([])
      const file = files[0]
      if (!file) {
        return
      }

      try {
        const { width, height } = await getImageDimensions(file)

        const errors: string[] = []

        if (minSizes) {
          const { width: minWidth, height: minHeight } = minSizes
          if (minWidth && width < minWidth) {
            errors.push('file-invalid-dimensions-width')
          }
          if (minHeight && height < minHeight) {
            errors.push('file-invalid-dimensions-height')
          }
        }

        if (width * height > UPLOAD_IMAGE_MAX_RESOLUTION) {
          errors.push('file-too-large-dimensions')
        }

        if (errors.length > 0) {
          setCustomErrors(errors)
          onError?.(errors)
        } else if (onDropOrSelected) {
          const image = Object.assign(file, { width, height })
          onDropOrSelected(image)
        }
      } catch {
        const error = ['file-invalid-type']
        setCustomErrors(error)
        onError?.(error)
      } finally {
        setIsDraggedOver(false)
      }
    }

    const { getRootProps, getInputProps, fileRejections } = useDropzone({
      accept: ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
      maxFiles: 1,
      maxSize: MAX_FILE_SIZE,
      onDragEnter: () => {
        setCustomErrors([])
        setIsDraggedOver(true)
      },
      onDragLeave: () => setIsDraggedOver(false),
      onDropAccepted: (files) => {
        void handleDrop(files)
      },
      onDropRejected: (files) => {
        const file = files[0]
        const errors = file.errors.map((e) => e.code)
        setHasInput(true)
        onError?.(errors)
        setIsDraggedOver(false)
      },
    })

    const rootProps = getRootProps()
    // role="presentation" on <div> is redundant,
    // input should be the only focusable element.
    delete rootProps.role
    delete rootProps.tabIndex

    const inputProps = getInputProps()
    // restore input focusability to allow keyboard navigation,
    // and let us define input style.
    inputProps.tabIndex = 0
    inputProps.disabled = disabled
    inputProps.id = useId()
    delete inputProps.style

    const errors = fileRejections.reduce(
      (acc, rejections) => {
        const { errors } = rejections

        acc.hasWrongType = errors.some((e) => e.code === 'file-invalid-type')
        acc.hasWrongSize = errors.some((e) => e.code === 'file-too-large')
        return acc
      },
      {
        hasWrongType: customErrors.includes('file-invalid-type'),
        hasWrongSize: false,
        hasWrongWidth: customErrors.includes('file-invalid-dimensions-width'),
        hasWrongHeight: customErrors.includes('file-invalid-dimensions-height'),
        hasWrongDimensions: customErrors.includes('file-too-large-dimensions'),
      }
    )
    const hasError =
      errors.hasWrongSize ||
      errors.hasWrongType ||
      errors.hasWrongWidth ||
      errors.hasWrongDimensions ||
      errors.hasWrongHeight

    const ariaId = useId()

    const errorMessage = (
      <>
        {hasInput && (
          <>
            <p>Erreurs: </p>
            {errors.hasWrongType && 'Le format de l’image n’est pas valide'}
            {errors.hasWrongSize && 'Le poids du fichier est trop lourd'}
            {errors.hasWrongDimensions &&
              "Image trop volumineuse. La résolution maximale acceptée est d'environ 80 millions de pixels (9000 x 9000 pixels)"}
            {minSizes?.height &&
              errors.hasWrongHeight &&
              `L’image doit faire au moins ${minSizes.height} pixels de haut`}
            {minSizes?.width &&
              errors.hasWrongWidth &&
              `L’image doit faire au moins ${minSizes.width} pixels de large`}
            {!hasError && <span>&nbsp;</span>}
          </>
        )}
        {!hasInput && <span>&nbsp;</span>}
      </>
    )
    return (
      <div className={cn(styles['image-drag-and-drop-container'])}>
        <div
          data-testid="image-drag-and-drop"
          {...rootProps}
          className={cn(
            styles['image-drag-and-drop'],
            {
              [styles['image-drag-and-drop-dragged-over']]: isDraggedOver,
              [styles['image-drag-and-drop-hovered']]: isHovered,
              [styles['image-drag-and-drop-focused']]: isFocused,
              [styles['image-drag-and-drop-error']]: hasError,
              [styles['image-drag-and-drop-disabled']]: disabled,
            },
            className
          )}
        >
          {isDraggedOver ? (
            <SvgIcon src={fullValidateIcon} alt="" width="24" />
          ) : (
            <SvgIcon
              src={strokePicture}
              alt=""
              width="58"
              viewBox="0 0 58 58"
            />
          )}
          <div className={styles['image-drag-and-drop-text']}>
            {isDraggedOver ? (
              'Déposez votre image ici'
            ) : (
              <>
                <p>Glissez et déposez votre image</p>
                <span>
                  {' ou '}
                  <label
                    id={`drag-and-drop-label-${ariaId}`}
                    className={styles['image-drag-and-drop-text-highlight']}
                    htmlFor={inputProps.id}
                  >
                    Importez une image
                  </label>
                  <input
                    {...inputProps}
                    ref={dragAndDropInputRef}
                    aria-labelledby={`drag-and-drop-label-${ariaId}`}
                    aria-describedby={`drag-and-drop-description-${ariaId}`}
                    aria-invalid={hasError ? 'true' : 'false'}
                    className={cn(styles['image-drag-and-drop-input'], {
                      [styles['image-drag-and-drop-input-error']]: hasError,
                      [styles['image-drag-and-drop-input-disabled']]: disabled,
                    })}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    data-testid="file-input"
                    onClick={(e) => {
                      e.stopPropagation()
                      setHasInput(false)

                      // Clear the input value to allow re-uploading the same file.
                      if (
                        dragAndDropInputRef &&
                        typeof dragAndDropInputRef !== 'function' &&
                        dragAndDropInputRef.current
                      ) {
                        dragAndDropInputRef.current.value = ''
                        dragAndDropInputRef.current.dispatchEvent(
                          new Event('input', { bubbles: true })
                        )
                      }

                      onClick?.()
                    }}
                  />
                </span>
              </>
            )}
          </div>
        </div>
        <div
          id={`drag-and-drop-description-${ariaId}`}
          className={styles['image-drag-and-drop-description']}
        >
          <div
            role="alert"
            aria-live="assertive"
            aria-atomic="true"
            className={styles['visually-hidden']}
          >
            {hasError ? errorMessage : <span>&nbsp;</span>}
          </div>
          <div className={styles['image-drag-and-drop-description']}>
            <ImageConstraintCheck
              label="Formats acceptés"
              constraint="JPG, JPEG, PNG, mpo, webP"
              hasInput={hasInput}
              hasError={errors.hasWrongType}
            />
            <ImageConstraintCheck
              label="Poids maximal du fichier"
              constraint="10 Mo"
              hasInput={hasInput}
              hasError={errors.hasWrongSize}
            />
            <ImageConstraintCheck
              label="Résolution maximale de l’image"
              constraint="80 Mégapixels"
              hasInput={hasInput}
              hasError={errors.hasWrongDimensions}
            />
            {minSizes?.height && (
              <ImageConstraintCheck
                label="Hauteur minimum"
                constraint={`${minSizes.height} px`}
                hasInput={hasInput}
                hasError={errors.hasWrongHeight}
              />
            )}
            {minSizes?.width && (
              <ImageConstraintCheck
                label="Largeur minimum"
                constraint={`${minSizes.width} px`}
                hasInput={hasInput}
                hasError={errors.hasWrongWidth}
              />
            )}
          </div>
        </div>
      </div>
    )
  }
)

ImageDragAndDrop.displayName = 'ImageDragAndDrop'
