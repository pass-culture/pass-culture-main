import cn from 'classnames'
import { useState } from 'react'
import { useDropzone } from 'react-dropzone'

import fullValidateIcon from 'icons/full-validate.svg'
import strokePicture from 'icons/stroke-picture.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ImageDragAndDrop.module.scss'

const ALLOWED_IMAGE_TYPES = [
  {
    mime: 'image/jpeg',
    extensions: ['.jpeg', '.jpg'],
  },
  {
    mime: 'image/png',
    extensions: ['.png'],
  },
  {
    mime: 'image/mpo',
    extensions: ['.mpo'],
  },
  {
    mime: 'image/webp',
    extensions: ['.webp'],
  },
]

const ImageConstraintCheck = ({
  label,
  constraint,
  hasError,
  errorMessage,
}: {
  label: string
  constraint: string
  hasError: boolean
  errorMessage: string
}) => {
  const imageConstraint = (
    <>
      {`${label} : `}
      <span className={styles['image-drag-and-drop-description-values']}>
        {constraint}
      </span>
    </>
  )

  return hasError ? (
    <span className={styles['image-drag-and-drop-description-error']}>
      <span className={styles['visually-hidden']}>{errorMessage}</span>
      {imageConstraint}
    </span>
  ) : (
    <span>{imageConstraint}</span>
  )
}

type FileWithDimensions = File & {
  width: number
  height: number
  objectUrlToBeRevoked?: string
}

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
  onError?: (err?: string) => void
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

export const ImageDragAndDrop = ({
  className,
  onClick,
  onDropOrSelected,
  onError,
  disabled,
  minSizes,
}: ImageDragAndDropProps) => {
  const [isDraggedOver, setIsDraggedOver] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const imageExtensions = ALLOWED_IMAGE_TYPES.reduce(
    (acc: string[], { extensions }) => {
      acc.push(...extensions)
      return acc
    },
    []
  )

  const imageMimeTypes = ALLOWED_IMAGE_TYPES.reduce(
    (acc: string[], { mime }) => {
      acc.push(mime)
      return acc
    },
    []
  )

  const { inputRef, getRootProps, getInputProps, fileRejections } = useDropzone(
    {
      accept: {
        'image/*': imageExtensions,
      },
      maxFiles: 1,
      maxSize: 10 * 1024 * 1024,
      onDragEnter: () => setIsDraggedOver(true),
      onDragLeave: () => setIsDraggedOver(false),
      onDropAccepted: (files) => {
        const file = files[0]
        // Disabled because untrue : file can be undefined at this point.
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
        if (file) {
          onDropOrSelected?.(file)
        }
        setIsDraggedOver(false)
      },
      onDropRejected: (files) => {
        const file = files[0]
        const error = file.errors[0].code
        onError?.(error)
        setIsDraggedOver(false)
      },
      getFilesFromEvent: (event) => {
        // @ts-expect-error: dataTransfer & target are actually existing properties.
        // An example of getFilesFromEvent can be found here :
        // https://react-dropzone.js.org/#section-extending-dropzone
        const fileList = event.dataTransfer?.files ?? event.target?.files
        const promises = []
        const files = []

        for (const file of fileList) {
          files.push(file)

          if (minSizes) {
            const promise: Promise<FileWithDimensions> = new Promise(
              (resolve) => {
                if (!imageMimeTypes.includes(file.type)) {
                  file.width = 0
                  file.height = 0
                  resolve(file)
                }

                const image = new Image()
                image.onload = () => {
                  file.width = image.width
                  file.height = image.height
                  file.objectUrlToBeRevoked = image.src
                  resolve(file)
                }
                image.src = URL.createObjectURL(file)
              }
            )

            promises.push(promise)
          }
        }

        return minSizes ? Promise.all(promises) : Promise.resolve(files)
      },
      validator: (file) => {
        const extendedFile = file as unknown as FileWithDimensions
        const { width, height, objectUrlToBeRevoked } = extendedFile
        const hasDimensions =
          extendedFile.width !== 0 && extendedFile.height !== 0

        // Additional validation to check image dimensions
        // when minSizes are provided.
        if (minSizes && hasDimensions) {
          const { width: minWidth, height: minHeight } = minSizes
          const isWidthInValid = minWidth ? width < minWidth : false
          const isHeightInValid = minHeight ? height < minHeight : false

          const errors = []

          if (isWidthInValid) {
            errors.push({
              code: 'file-invalid-dimensions-width',
              message: `L’image doit faire au moins ${minWidth} pixels de large`,
            })
          }

          if (isHeightInValid) {
            errors.push({
              code: 'file-invalid-dimensions-height',
              message: `L’image doit faire au moins ${minHeight} pixels de haut`,
            })
          }

          // Revoke the object URL we created previously to get image dimensions,
          // and avoid memory leaks.
          if (objectUrlToBeRevoked) {
            URL.revokeObjectURL(objectUrlToBeRevoked)
          }

          return errors.length > 0 ? errors : null
        }

        return null
      },
    }
  )

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
  delete inputProps.style

  const errors = fileRejections.reduce(
    (acc, rejections) => {
      const { errors } = rejections

      acc.hasWrongType = errors.some((e) => e.code === 'file-invalid-type')
      acc.hasWrongSize = errors.some((e) => e.code === 'file-too-large')
      acc.hasWrongWidth = errors.some(
        (e) => e.code === 'file-invalid-dimensions-width'
      )
      acc.hasWrongHeight = errors.some(
        (e) => e.code === 'file-invalid-dimensions-height'
      )

      return acc
    },
    {
      hasWrongType: false,
      hasWrongSize: false,
      hasWrongWidth: false,
      hasWrongHeight: false,
    }
  )
  const hasError =
    errors.hasWrongSize ||
    errors.hasWrongType ||
    errors.hasWrongWidth ||
    errors.hasWrongHeight

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
          <SvgIcon src={strokePicture} alt="" width="58" viewBox="0 0 58 58" />
        )}
        <div className={styles['image-drag-and-drop-text']}>
          {isDraggedOver ? (
            <>Déposez votre image ici</>
          ) : (
            <>
              <span>Glissez et déposez votre image</span>
              <span>
                {' ou '}
                <label
                  id="drag-and-drop-label"
                  className={styles['image-drag-and-drop-text-highlight']}
                >
                  Importez une image
                </label>
                <input
                  {...inputProps}
                  aria-labelledby="drag-and-drop-label"
                  aria-describedby="drag-and-drop-description"
                  aria-invalid={hasError}
                  className={cn(styles['image-drag-and-drop-input'], {
                    [styles['image-drag-and-drop-input-error']]: hasError,
                    [styles['image-drag-and-drop-input-disabled']]: disabled,
                  })}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onClick={(e) => {
                    e.stopPropagation()

                    // Clear the input value to allow re-uploading the same file.
                    if (inputRef.current) {
                      inputRef.current.value = ''
                      inputRef.current.dispatchEvent(
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
        id="drag-and-drop-description"
        className={styles['image-drag-and-drop-description']}
        role="alert"
        aria-relevant="additions"
      >
        <ImageConstraintCheck
          label="Formats acceptés"
          constraint="JPG, JPEG, PNG, mpo, webP"
          hasError={errors.hasWrongType}
          errorMessage="Le format de l’image n’est pas valide"
        />
        <ImageConstraintCheck
          label="Poids maximal du fichier"
          constraint="10 Mo"
          hasError={errors.hasWrongSize}
          errorMessage="Le poids du fichier est trop lourd"
        />
        {minSizes?.height && (
          <ImageConstraintCheck
            label="Hauteur minimum"
            constraint={`${minSizes.height} px`}
            hasError={errors.hasWrongHeight}
            errorMessage={`L’image doit faire au moins ${minSizes.height} pixels de haut`}
          />
        )}
        {minSizes?.width && (
          <ImageConstraintCheck
            label="Largeur minimum"
            constraint={`${minSizes.width} px`}
            hasError={errors.hasWrongWidth}
            errorMessage={`L’image doit faire au moins ${minSizes.width} pixels de large`}
          />
        )}
      </div>
    </div>
  )
}
