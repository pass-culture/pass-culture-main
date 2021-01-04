import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import ThumbnailDialog from 'components/pages/Offer/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnail = ({ url }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)

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
          src={url}
        />
      </button>

      {isModalOpened && <ThumbnailDialog setIsModalOpened={setIsModalOpened} />}
    </>
  )
}

OfferThumbnail.propTypes = {
  url: PropTypes.string.isRequired,
}

export default OfferThumbnail
