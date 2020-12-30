import React from 'react'

import { ReactComponent as AddThumbnail } from './assets/add-thumbnail.svg'

const OfferThumbnailPlaceholder = () => (
  <button
    className="of-placeholder"
    type="button"
  >
    <AddThumbnail />
    {'Ajouter une image'}
  </button>
)

export default OfferThumbnailPlaceholder
