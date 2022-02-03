import React, { FunctionComponent } from 'react'

import { OfferHomePreview } from './OfferHomePreview/OfferHomePreview'
import { OfferPreview } from './OfferPreview/OfferPreview'

interface Props {
  preview: string
}

export const ImagePreview: FunctionComponent<Props> = ({ preview }) => (
  <div className="image-preview-previews">
    <OfferHomePreview previewImageURI={preview} />
    <OfferPreview previewImageURI={preview} />
  </div>
)
