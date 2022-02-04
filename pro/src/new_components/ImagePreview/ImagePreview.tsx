import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from './assets/mobile-shell.svg'

interface ImagePreviewScreenProps {
  title: string
}

export const ImagePreview: FunctionComponent<ImagePreviewScreenProps> = ({
  title,
  children,
}) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    {children}
    <div>{title}</div>
  </div>
)
