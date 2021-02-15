import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddThumbnailIcon } from 'components/pages/Offer/Offer/OfferDetails/OfferThumbnail/OfferThumbnailPlaceholder/assets/add-thumbnail.svg'
import ThumbnailDialog from 'components/pages/Offer/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnailPlaceholder = ({ setThumbnailInfo }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)
  const [preview, setPreview] = useState()

  const openModal = useCallback(() => {
    setIsModalOpened(true)
  }, [])

  return (
    <>
      <button
        className={`of-placeholder ${preview ? 'of-image' : ''}`}
        onClick={openModal}
        title={`${preview ? "Modifier l'image" : 'Ajouter une image'}`}
        type="button"
      >
        {preview ? (
          <Icon
            alt="Image de l'offre"
            src={preview}
          />
        ) : (
          <>
            <AddThumbnailIcon />
            {'Ajouter une image'}
          </>
        )}
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

OfferThumbnailPlaceholder.propTypes = {
  setThumbnailInfo: PropTypes.func.isRequired,
}

export default OfferThumbnailPlaceholder
