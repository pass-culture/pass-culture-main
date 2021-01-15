import React, { useCallback, useState } from 'react'

import { ReactComponent as AddThumbnailIcon } from 'components/pages/Offer/Offer/OfferDetails/OfferThumbnail/OfferThumbnailPlaceholder/assets/add-thumbnail.svg'
import ThumbnailDialog from 'components/pages/Offer/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnailPlaceholder = () => {
  const [isModalOpened, setIsModalOpened] = useState(false)

  const openModal = useCallback(() => {
    setIsModalOpened(true)
  }, [])

  return (
    <>
      <button
        className="of-placeholder"
        onClick={openModal}
        title="Ajouter une image"
        type="button"
      >
        <AddThumbnailIcon />
        {'Ajouter une image'}
      </button>

      {isModalOpened && <ThumbnailDialog setIsModalOpened={setIsModalOpened} />}
    </>
  )
}

export default OfferThumbnailPlaceholder
