import classNames from 'classnames'
import type { RefCallback } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import type { FileUploadStatus } from '@/design-system/FilesUpload/types'
import { formatFileSize } from '@/design-system/UploadZone/utils'
import fullErrorIcon from '@/icons/full-error.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './FileUploadItem.module.scss'

const STATUSES: Record<FileUploadStatus, { icon: string; label: string }> = {
  success: { icon: fullValidateIcon, label: 'Fichier ajouté' },
  error: {
    icon: fullErrorIcon,
    label:
      'Une erreur est survenue. Veuillez télécharger à nouveau le fichier.',
  },
}

type FileUploadItemProps = {
  file: File
  status?: FileUploadStatus
  disabled?: boolean
  onDelete: () => void
  deleteButtonRef?: RefCallback<HTMLElement>
}

export function FileUploadItem({
  file,
  status,
  disabled = false,
  onDelete,
  deleteButtonRef,
}: Readonly<FileUploadItemProps>) {
  return (
    <li className={styles['file-upload-item']}>
      <div className={styles['content']}>
        <p className={styles['name']}>{file.name}</p>
        <div className={styles['details']}>
          <p className={styles['size']}>{formatFileSize(file.size)}</p>
          {/* Always rendered so that status changes are announced. */}
          <output
            className={classNames(styles['status'], {
              [styles[`status-${status}`]]: status,
            })}
          >
            {status && (
              <>
                <SvgIcon
                  src={STATUSES[status].icon}
                  alt=""
                  className={styles['status-icon']}
                />
                {STATUSES[status].label}
              </>
            )}
          </output>
        </div>
      </div>
      <Button
        ref={deleteButtonRef}
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        icon={fullTrashIcon}
        aria-label={`Supprimer ${file.name}`}
        disabled={disabled}
        onClick={onDelete}
      />
    </li>
  )
}
