import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useRef } from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddThumbnailIcon } from 'components/pages/Offers/Offer/OfferDetails/OfferThumbnail/assets/add-thumbnail.svg'
import { ReactComponent as ErrorAlertIcon } from 'components/pages/Offers/Offer/OfferDetails/OfferThumbnail/assets/error-alert.svg'
import ThumbnailDialog from 'components/pages/Offers/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnail = ({ isDisabled, setThumbnailInfo, thumbnailError, url }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)
  const [preview, setPreview] = useState(url)
  const thumbnailButtonRef = useRef(null)

  const openModal = useCallback(e => {
    e.target.blur()
    setIsModalOpened(true)
  }, [])

  useEffect(() => {
    if (thumbnailError) {
      setPreview(url)
      if (thumbnailButtonRef.current) {
        thumbnailButtonRef.current.scrollIntoView()
      }
    }
  }, [thumbnailError, url])

  return (
    <>
      <button
        className={`of-placeholder
        ${preview ? 'of-image' : ''}
        ${thumbnailError ? 'of-thumbnail-error' : ''}`}
        disabled={isDisabled}
        onClick={openModal}
        ref={thumbnailButtonRef}
        title={`${preview ? 'Modifier l’image' : 'Ajouter une image'}`}
        type="button"
      >
        {preview ? (
          <Icon
            alt="Image de l’offre"
            src={preview}
          />
        ) : (
          <>
            <AddThumbnailIcon />
            {'Ajouter une image'}
          </>
        )}

        {thumbnailError && (
          <span className="of-error-message">
            <ErrorAlertIcon />
            {"L'image n'a pas pu être ajoutée. Veuillez réessayer."}
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

OfferThumbnail.defaultProps = {
  isDisabled: false,
  url: null,
}

OfferThumbnail.propTypes = {
  isDisabled: PropTypes.bool,
  setThumbnailInfo: PropTypes.func.isRequired,
  thumbnailError: PropTypes.bool.isRequired,
  url: PropTypes.string,
}

export default OfferThumbnail
