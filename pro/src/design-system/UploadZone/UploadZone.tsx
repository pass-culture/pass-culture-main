import classNames from 'classnames'
import {
  type FocusEventHandler,
  type MouseEvent,
  type Ref,
  useId,
  useImperativeHandle,
  useState,
} from 'react'
import {
  type Accept,
  ErrorCode,
  type FileError,
  type FileRejection,
  useDropzone,
} from 'react-dropzone'

import { useFormLayoutSideComponentDescribedBy } from '@/commons/context/FormLayoutSideComponentContext/FormLayoutSideComponentContext'
import { FieldHeader } from '@/design-system/common/FieldHeader/FieldHeader'
import type { RequiredIndicator } from '@/design-system/common/types'
import fullErrorIcon from '@/icons/full-error.svg'
import strokeShareIcon from '@/icons/stroke-share.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './UploadZone.module.scss'
import { getConditionsText } from './utils'

const FILE_CORRUPTED_ERROR_CODE = 'file-corrupted'

export type UploadZoneLabelProps =
  | {
      /** Label of the field */
      label: string
      /** Description displayed under the label (requires a label) */
      description?: string
    }
  | { label?: never; description?: never }

export type UploadZoneBaseProps = {
  /** Name of the file input */
  name?: string
  /** Id of the file input */
  id?: string
  /** Typography of the label, defaults to 'body' */
  labelVariant?: 'body' | 'title3'
  required?: boolean
  requiredIndicator?: RequiredIndicator
  /** Icon displayed in the zone, defaults to the "share" icon */
  icon?: string
  /** Accepted MIME types, each one mapped to its extensions (e.g. `{ 'application/pdf': ['.pdf'] }`) */
  accept?: Accept
  /** Maximum size of a file, in bytes */
  maxSize?: number
  /**
   * Help text displayed in the zone. Defaults to the accepted formats and the maximum size
   * built from `accept` and `maxSize`. Use `getConditionsText` to add a condition to the default text,
   * or an empty string to hide it.
   */
  conditionsText?: string
  /** Maximum number of files */
  maxFiles?: number
  /**
   * Number of files already added. Only set by `FilesUpload`: with `maxFiles`, it displays
   * the files counter, which must stay hidden when the zone is used alone.
   */
  filesCount?: number
  disabled?: boolean
  /** Error message coming from the form (e.g. a required field) */
  error?: string
  /** Callback triggered with the files that passed the validation */
  onFilesAdded?: (files: File[]) => void
  /**
   * Callback triggered with the files rejected by the validation, whose errors are displayed by the zone
   * (e.g. to clear an error previously set through `error`)
   */
  onFilesRejected?: (files: File[]) => void
  onBlur?: FocusEventHandler<HTMLInputElement>
  describedBy?: string
  /** Ref of the file input (e.g. the `field.ref` of react-hook-form, to focus it on error) */
  ref?: Ref<HTMLInputElement>
}

export type UploadZoneProps = UploadZoneBaseProps & UploadZoneLabelProps

const validateFileIsReadable = async (
  file: File
): Promise<FileError | null> => {
  try {
    await file.slice(0, 1).arrayBuffer()
    return null
  } catch {
    return { code: FILE_CORRUPTED_ERROR_CODE, message: 'Unreadable file' }
  }
}

const getRejectionMessage = (
  code: FileError['code'],
  maxFiles?: number
): string | null => {
  switch (code) {
    case ErrorCode.FileInvalidType:
      return 'Le format du fichier n’est pas accepté.'
    case ErrorCode.FileTooLarge:
      return 'Le fichier est trop lourd.'
    case ErrorCode.FileTooSmall:
    case FILE_CORRUPTED_ERROR_CODE:
      return 'Le fichier est vide ou corrompu.'
    case ErrorCode.TooManyFiles:
      return maxFiles === 1
        ? 'Vous ne pouvez ajouter qu’un seul fichier.'
        : `Vous ne pouvez pas ajouter plus de ${maxFiles} fichiers.`
    default:
      return null
  }
}

const getRejectionMessages = (
  fileRejections: readonly FileRejection[],
  maxFiles?: number
): string[] =>
  fileRejections
    .flatMap(({ errors }) => errors)
    .map(({ code }) => getRejectionMessage(code, maxFiles))
    .filter((message): message is string => message !== null)

export const UploadZone = ({
  name,
  id,
  label,
  labelVariant = 'body',
  description,
  required = false,
  requiredIndicator = 'symbol',
  icon = strokeShareIcon,
  accept,
  maxSize,
  conditionsText = getConditionsText(accept, maxSize),
  maxFiles,
  filesCount,
  disabled = false,
  error,
  onFilesAdded,
  onFilesRejected,
  onBlur,
  describedBy,
  ref,
}: UploadZoneProps) => {
  const formLayoutDescribedBy = useFormLayoutSideComponentDescribedBy()
  const uploadZoneId = useId()
  const inputId = id ?? uploadZoneId
  const labelId = useId()
  const descriptionId = useId()
  const instructionId = useId()
  const conditionsId = useId()
  const counterId = useId()
  const errorsId = useId()
  const rejectionPrefixId = useId()

  const [rejectionMessages, setRejectionMessages] = useState<string[]>([])

  const remainingFilesCount =
    maxFiles === undefined
      ? undefined
      : Math.max(maxFiles - (filesCount ?? 0), 0)
  const isMaxFilesReached = remainingFilesCount === 0
  const hasFilesCounter = maxFiles !== undefined && filesCount !== undefined

  const { getRootProps, getInputProps, isDragActive, inputRef } = useDropzone({
    accept,
    maxSize,
    // Empty files are rejected as corrupted.
    minSize: 1,
    maxFiles: remainingFilesCount,
    multiple: maxFiles !== 1,
    disabled: disabled || isMaxFilesReached,
    // The native input covers the whole zone and handles clicks and keyboard by itself.
    noClick: true,
    noKeyboard: true,
    validator: validateFileIsReadable,
    onDragEnter: () => setRejectionMessages([]),
    onDrop: (acceptedFiles, fileRejections) => {
      setRejectionMessages(getRejectionMessages(fileRejections, maxFiles))

      if (fileRejections.length > 0) {
        inputRef.current?.focus({ preventScroll: true })
        onFilesRejected?.(fileRejections.map(({ file }) => file))
      }
      if (acceptedFiles.length > 0) {
        onFilesAdded?.(acceptedFiles)
      }
    },
  })

  useImperativeHandle(ref, () => inputRef.current)

  const rootProps = getRootProps()
  // The input is the only interactive element: no role nor state on its container.
  delete rootProps.role
  delete rootProps['aria-disabled']

  const inputProps = getInputProps()
  // Restore the input focusability and remove react-dropzone defaults
  // (hidden style, generic aria-label).
  delete inputProps.style
  delete inputProps.tabIndex
  delete inputProps['aria-label']

  const handleInputClick = (event: MouseEvent<HTMLInputElement>) => {
    // When the maximum number of files is reached, the input stays focusable
    // (so that the files counter is read) but must not open the file picker.
    if (isMaxFilesReached) {
      event.preventDefault()
      return
    }
    // Allows selecting again a file that has been removed.
    event.currentTarget.value = ''
  }

  const errors = [...new Set([...rejectionMessages, error ?? ''])].filter(
    Boolean
  )
  const hasError = errors.length > 0
  const errorIds = errors.map((_, index) => `${errorsId}-${index}`)
  const rejectionErrorIds = errorIds.filter((_, index) =>
    rejectionMessages.includes(errors[index])
  )
  const formErrorIds = errorIds.filter(
    (errorId) => !rejectionErrorIds.includes(errorId)
  )

  // The files rejected by the zone are announced in the input name, right after
  // the label and before the native value of the input ("Aucun fichier choisi").
  const labelledByIds = [
    label ? labelId : instructionId,
    ...(rejectionErrorIds.length > 0
      ? [rejectionPrefixId, ...rejectionErrorIds]
      : []),
  ].join(' ')

  const describedByIds = [
    description ? descriptionId : '',
    conditionsText ? conditionsId : '',
    hasFilesCounter ? counterId : '',
    ...formErrorIds,
    describedBy ?? '',
    formLayoutDescribedBy ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={styles['upload-zone']}>
      {label && (
        <div className={styles['header']}>
          <FieldHeader
            fieldId={inputId}
            label={label}
            labelId={labelId}
            labelVariant={labelVariant}
            description={description}
            descriptionId={descriptionId}
            required={required}
            requiredIndicator={requiredIndicator}
          />
        </div>
      )}
      <div
        {...rootProps}
        className={classNames(styles['zone'], {
          [styles['zone-dragged-over']]: isDragActive,
          [styles['zone-disabled']]: disabled || isMaxFilesReached,
          [styles['zone-error']]: hasError,
        })}
      >
        <SvgIcon src={icon} alt="" className={styles['zone-icon']} />
        <div className={styles['zone-texts']}>
          <p
            id={instructionId}
            className={styles['zone-instruction']}
            aria-hidden="true"
          >
            {isDragActive
              ? 'Déposez votre fichier ici'
              : 'Importez ou déposez le fichier ici'}
          </p>
          {conditionsText && (
            // Only read through the description of the file input, which comes after it.
            <p
              id={conditionsId}
              className={styles['zone-conditions']}
              aria-hidden="true"
            >
              {conditionsText}
            </p>
          )}
        </div>
        <input
          {...inputProps}
          // Not passed through getInputProps, which drops handlers when the dropzone is disabled.
          onClick={handleInputClick}
          onBlur={onBlur}
          id={inputId}
          name={name}
          className={styles['zone-input']}
          disabled={disabled}
          aria-labelledby={labelledByIds}
          aria-describedby={describedByIds || undefined}
          aria-invalid={hasError}
          aria-required={required}
          aria-disabled={(!disabled && isMaxFilesReached) || undefined}
        />
      </div>
      <div
        className={classNames(styles['footer'], {
          [styles['has-footer']]: hasError || hasFilesCounter,
        })}
      >
        <div role="alert" className={styles['errors']}>
          {hasError && (
            <div className={styles['errors-list']}>
              {rejectionErrorIds.length > 0 && (
                <p id={rejectionPrefixId} className={styles['visually-hidden']}>
                  Le fichier choisi est non conforme :
                </p>
              )}
              {errors.map((errorMessage, index) => (
                <p
                  key={errorMessage}
                  id={errorIds[index]}
                  className={styles['error']}
                >
                  <SvgIcon
                    src={fullErrorIcon}
                    alt=""
                    className={styles['error-icon']}
                  />
                  {errorMessage}
                </p>
              ))}
            </div>
          )}
        </div>
        {hasFilesCounter && (
          <p id={counterId} className={styles['counter']}>
            {filesCount}/{maxFiles} {maxFiles > 1 ? 'fichiers' : 'fichier'}{' '}
            maximum
          </p>
        )}
      </div>
    </div>
  )
}
