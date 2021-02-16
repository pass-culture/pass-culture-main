import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import ThumbnailDialog from 'components/pages/Offers/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnail = ({ setThumbnailInfo, url }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)
  const [preview, setPreview] = useState(url)

  const openModal = useCallback(() => {
    setIsModalOpened(true)
  }, [])

  return (
    <>
      <button
        className="of-placeholder of-image"
        onClick={openModal}
        title="Modifier l’image"
        type="button"
      >
        <Icon
          alt="Image de l’offre"
          src={preview}
        />
      </button>

      {isModalOpened && (
        <ThumbnailDialog
          setIsModalOpened={setIsModalOpened}
          setPreview={setPreview}
          setThumbnailInfo={setThumbnailInfo}
        />
      )}
    </>
  )
}

OfferThumbnail.propTypes = {
  setThumbnailInfo: PropTypes.func.isRequired,
  url: PropTypes.string.isRequired,
}

export default OfferThumbnail
