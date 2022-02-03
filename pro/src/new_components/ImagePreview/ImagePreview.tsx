import React, { FunctionComponent } from 'react'

import { OfferHomePreview } from './OfferHomePreview/OfferHomePreview'
import { OfferPreview } from './OfferPreview/OfferPreview'
import { ImagePreviewMode, ImagePreviewScreenProps } from './types'
import { VenueHomePreview } from './VenueHomePreview/VenueHomePreview'
import { VenuePreview } from './VenuePreview/VenuePreview'

interface Props {
  preview: string
  mode: ImagePreviewMode
}

const getImagePreviewScreens = (
  mode: ImagePreviewMode
): FunctionComponent<ImagePreviewScreenProps>[] => {
  switch (mode) {
    case ImagePreviewMode.OFFER:
      return [OfferHomePreview, OfferPreview]
    case ImagePreviewMode.VENUE:
      return [VenueHomePreview, VenuePreview]
  }
}

export const ImagePreview: FunctionComponent<Props> = ({ preview, mode }) => (
  <div className="image-preview-previews">
    {getImagePreviewScreens(mode).map(PreviewScreen => (
      <PreviewScreen key={PreviewScreen.name} previewImageURI={preview} />
    ))}
  </div>
)
