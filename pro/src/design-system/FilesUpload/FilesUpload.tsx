import { useImperativeHandle, useRef, useState } from 'react'

import type { FileUploadStatus } from '@/design-system/FilesUpload/types'
import {
  UploadZone,
  type UploadZoneBaseProps,
  type UploadZoneLabelProps,
} from '@/design-system/UploadZone/UploadZone'

import styles from './FilesUpload.module.scss'
import { FileUploadItem } from './FileUploadItem/FileUploadItem'

// File objects have no identifier: give each one a stable id to use as a list key.
const fileIds = new WeakMap<File, string>()
let lastFileId = 0
const getFileId = (file: File): string => {
  let fileId = fileIds.get(file)
  if (!fileId) {
    lastFileId++
    fileId = `file-${lastFileId}`
    fileIds.set(file, fileId)
  }
  return fileId
}

export type FilesUploadProps = Omit<
  UploadZoneBaseProps,
  'filesCount' | 'onFilesAdded'
> &
  UploadZoneLabelProps & {
    /** Files of the field, when controlled (e.g. by a react-hook-form `Controller`) */
    value?: File[]
    /** Callback triggered with the whole list of files, after an addition or a deletion */
    onChange?: (files: File[]) => void
    /** Status of a file, handled by the feature (e.g. after sending it to the server) */
    getFileStatus?: (file: File) => FileUploadStatus | undefined
  }

/**
 * Upload zone followed by the list of the added files.
 * The files are sent to the feature through `onChange`, to be used on submit:
 *
 * @example
 * <Controller
 *   control={control}
 *   name="documents"
 *   render={({ field, fieldState }) => (
 *     <FilesUpload
 *       {...field}
 *       label="Justificatifs"
 *       error={fieldState.error?.message}
 *       accept={{ 'application/pdf': ['.pdf'] }}
 *       maxSize={5_000_000}
 *       maxFiles={3}
 *     />
 *   )}
 * />
 */
export const FilesUpload = ({
  value,
  onChange,
  getFileStatus,
  disabled = false,
  ref,
  ...uploadZoneProps
}: FilesUploadProps) => {
  const [uncontrolledFiles, setUncontrolledFiles] = useState<File[]>([])
  const files = value ?? uncontrolledFiles

  const uploadZoneInputRef = useRef<HTMLInputElement>(null)
  const deleteButtonsRef = useRef(new Map<string, HTMLElement>())

  useImperativeHandle(ref, () => uploadZoneInputRef.current as HTMLInputElement)

  const updateFiles = (newFiles: File[]) => {
    if (value === undefined) {
      setUncontrolledFiles(newFiles)
    }
    onChange?.(newFiles)
  }

  const deleteFile = (fileToDelete: File) => {
    // Keep the focus in the list: on the next file, else on the previous one,
    // else on the upload zone.
    const index = files.indexOf(fileToDelete)
    const nextFile = files[index + 1] ?? files[index - 1]
    const elementToFocus = nextFile
      ? deleteButtonsRef.current.get(getFileId(nextFile))
      : uploadZoneInputRef.current

    updateFiles(files.filter((file) => file !== fileToDelete))
    elementToFocus?.focus()
  }

  return (
    <div className={styles['files-upload']}>
      <UploadZone
        {...uploadZoneProps}
        ref={uploadZoneInputRef}
        disabled={disabled}
        filesCount={files.length}
        onFilesAdded={(addedFiles) => updateFiles([...files, ...addedFiles])}
      />
      {files.length > 0 && (
        <ul className={styles['files-list']} aria-label="Fichiers ajoutés">
          {files.map((file) => {
            const fileId = getFileId(file)

            return (
              <FileUploadItem
                key={fileId}
                file={file}
                status={getFileStatus?.(file)}
                disabled={disabled}
                onDelete={() => deleteFile(file)}
                deleteButtonRef={(element) => {
                  if (element) {
                    deleteButtonsRef.current.set(fileId, element)
                  } else {
                    deleteButtonsRef.current.delete(fileId)
                  }
                }}
              />
            )
          })}
        </ul>
      )}
    </div>
  )
}
