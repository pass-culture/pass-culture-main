import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import ThumbnailDialog from 'components/pages/Offers/Offer/Thumbnail/ThumbnailDialog'

import { ReactComponent as ErrorAlertThumbnail } from './OfferThumbnailPlaceholder/assets/error-alert.svg'

const OfferThumbnail = ({ setThumbnailInfo, thumbnailError, url }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)
  const [preview, setPreview] = useState(url)

  const openModal = useCallback(e => {
    e.target.blur()
    setIsModalOpened(true)
  }, [])

  useEffect(() => {
    if (thumbnailError) {
      setPreview(url)
    }
  }, [thumbnailError, url])

  return (
    <>
      <button
        className={`of-placeholder of-image ${thumbnailError ? 'of-error-upload-image' : ''}`}
        onClick={openModal}
        title="Modifier l’image"
        type="button"
      >
        <Icon
          alt="Image de l’offre"
          src={preview}
        />
        {thumbnailError && (
          <span className="of-error-message">
            <ErrorAlertThumbnail />
            {"L'image n'a pas pu être ajoutée. Veuillez réessayer"}
          </span>
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

OfferThumbnail.propTypes = {
  setThumbnailInfo: PropTypes.func.isRequired,
  thumbnailError: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
}

export default OfferThumbnail
