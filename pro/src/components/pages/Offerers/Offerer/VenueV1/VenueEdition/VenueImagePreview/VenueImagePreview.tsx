import React, { FunctionComponent } from 'react'

import { ImagePreview } from 'new_components/ImagePreview/ImagePreview'
import { ImagePreviewMode } from 'new_components/ImagePreview/types'

interface Props {
  preview: string
}

export const VenueImagePreview: FunctionComponent<Props> = ({ preview }) => (
  <ImagePreview mode={ImagePreviewMode.VENUE} preview={preview} />
)
