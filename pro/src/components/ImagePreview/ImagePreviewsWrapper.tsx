import React, { FunctionComponent } from 'react'

interface Props {
  children?: React.ReactNode
}

export const ImagePreviewsWrapper: FunctionComponent<Props> = ({
  children,
}) => <div className="image-preview-previews">{children}</div>
