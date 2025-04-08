import React, { FunctionComponent } from 'react'

import styles from './ImagePreview.module.scss'
interface Props {
  children?: React.ReactNode
}

export const ImagePreviewsWrapper: FunctionComponent<Props> = ({
  children,
}) => (
  <div className={styles['image-preview-previews']}>
    <p className={styles['image-preview-previews-title']}>
      Prévisualisation de votre image dans l’application pass Culture
    </p>
    <div className={styles['image-preview-previews-container']}>{children}</div>
  </div>
)
