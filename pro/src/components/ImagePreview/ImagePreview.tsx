import React, { FunctionComponent } from 'react'

import mobileShell from './assets/mobile-shell.svg'
import styles from './ImagePreview.module.scss'

interface ImagePreviewScreenProps {
  title: string
  children?: React.ReactNode
}

export const ImagePreview: FunctionComponent<ImagePreviewScreenProps> = ({
  title,
  children,
}) => (
  <figure className={styles['image-preview-previews-wrapper']}>
    <img
      src={mobileShell}
      alt=""
      className={styles['image-preview-previews-shell']}
    />
    <div className={styles['image-preview-screen']}>{children}</div>
    <figcaption>{title}</figcaption>
  </figure>
)
