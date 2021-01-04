import React from 'react'

import { ReactComponent as AddThumbnailIcon } from './assets/add-thumbnail.svg'

const OfferThumbnailPlaceholder = () => (
  <button
    className="of-placeholder"
    type="button"
  >
    <AddThumbnailIcon />
    {'Ajouter une image'}
  </button>
)

export default OfferThumbnailPlaceholder
