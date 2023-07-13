import React, { FunctionComponent } from 'react'

import styles from './ImagePreview.module.scss'
interface Props {
  children?: React.ReactNode
}

export const ImagePreviewsWrapper: FunctionComponent<Props> = ({
  children,
}) => <div className={styles['image-preview-previews']}>{children}</div>
