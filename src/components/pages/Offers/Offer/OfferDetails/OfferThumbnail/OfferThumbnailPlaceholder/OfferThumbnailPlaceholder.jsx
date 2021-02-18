import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddThumbnailIcon } from 'components/pages/Offers/Offer/OfferDetails/OfferThumbnail/OfferThumbnailPlaceholder/assets/add-thumbnail.svg'
import { ReactComponent as ErrorAlertThumbnail } from 'components/pages/Offers/Offer/OfferDetails/OfferThumbnail/OfferThumbnailPlaceholder/assets/error-alert.svg'
import ThumbnailDialog from 'components/pages/Offers/Offer/Thumbnail/ThumbnailDialog'

const OfferThumbnailPlaceholder = ({ setThumbnailInfo }) => {
  const [isModalOpened, setIsModalOpened] = useState(false)
  const [preview, setPreview] = useState()

  const openModal = useCallback(e => {
    e.target.blur()
    setIsModalOpened(true)
  }, [])

  return (
    <>
      <button
        className={`of-placeholder of-error-upload-image ${preview ? 'of-image' : ''}`}
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
            <div className="of-error-message">
              <ErrorAlertThumbnail />
              {"L'image n'a pas pu être ajoutée. Veuillez réessayer"}
            </div>
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
