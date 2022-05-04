import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from './assets/mobile-shell.svg'

interface ImagePreviewScreenProps {
  title: string
  children?: React.ReactNode
}

export const ImagePreview: FunctionComponent<ImagePreviewScreenProps> = ({
  title,
  children,
}) => (
  <figure className="image-preview-previews-wrapper">
    <MobileShell />
    <div className="image-preview-screen">{children}</div>
    <figcaption>{title}</figcaption>
  </figure>
)
