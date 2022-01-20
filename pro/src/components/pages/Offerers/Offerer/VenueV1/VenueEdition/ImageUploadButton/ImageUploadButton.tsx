import React, { FunctionComponent } from 'react'

import { ReactComponent as PlusIcon } from './assets/plus-icon.svg'
import styles from './ImageUploadButton.module.scss'

export type ImageUploadButtonProps = {
  onClick: () => void
}

export const ImageUploadButton: FunctionComponent<ImageUploadButtonProps> = ({
  onClick,
}) => (
  <button
    className={styles['image-upload-button']}
    onClick={onClick}
    type="button"
  >
    <PlusIcon className={styles['image-upload-button-icon']} />
    <span className={styles['image-upload-button-label']}>
      Ajouter une image
    </span>
  </button>
)
