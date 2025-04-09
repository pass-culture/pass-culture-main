import cn from 'classnames'
import { useState } from 'react'
import { useDropzone } from 'react-dropzone'

import fullValidateIcon from 'icons/full-validate.svg'
import strokePicture from 'icons/stroke-picture.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ImageDragAndDrop.module.scss'

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

interface ImageDragAndDropProps {
  /**
   * Callback triggered when a file is dropped or selected.
   */
  onDropOrSelected?: (file: File) => void
  /**
   * Callback triggered when an error occurs, e.g. wrong file type or size.
   */
  onError?: (err?: string) => void
}

export const ImageDragAndDrop = ({
  onDropOrSelected,
  onError,
}: ImageDragAndDropProps) => {
  const [isDraggedOver, setIsDraggedOver] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const { getRootProps, getInputProps, fileRejections } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.mpo', '.webp'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    onDrop: (acceptedFiles, fileRejections) => {
      const file = acceptedFiles[0]

      // Disabled because untrue : file can be undefined at this point.
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      if (file) {
        onDropOrSelected?.(file)
      } else {
        const error = fileRejections[0]?.errors[0].code
        onError?.(error)
      }
    },
    onDragEnter: () => setIsDraggedOver(true),
    onDragLeave: () => setIsDraggedOver(false),
    onDropAccepted: () => setIsDraggedOver(false),
    onDropRejected: () => setIsDraggedOver(false),
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
  delete inputProps.style

  const errors = fileRejections.reduce(
    (acc, rejections) => {
      const { errors } = rejections

      acc.hasWrongType = errors.some((e) => e.code === 'file-invalid-type')
      acc.hasWrongSize = errors.some((e) => e.code === 'file-too-large')

      return acc
    },
    {
      hasWrongType: false,
      hasWrongSize: false,
    }
  )
  const hasError = errors.hasWrongSize || errors.hasWrongType

  return (
    <>
      <div
        data-testid="image-drag-and-drop"
        {...rootProps}
        className={cn(styles['image-drag-and-drop'], {
          [styles['image-drag-and-drop-dragged-over']]: isDraggedOver,
          [styles['image-drag-and-drop-hovered']]: isHovered,
          [styles['image-drag-and-drop-focused']]: isFocused,
          [styles['image-drag-and-drop-error']]: hasError,
        })}
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
                  })}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
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
      </div>
    </>
  )
}
