import React from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { getIndividualOfferImage } from 'screens/IndividualOffer/utils/getIndividualOfferImage'

import style from './OfferAppPreview.module.scss'
import { OptionsIcons } from './OptionsIcons'
import { VenueDetails } from './VenueDetails'

interface OfferAppPreviewProps {
  offer: GetIndividualOfferResponseModel
}

const OfferAppPreview = ({ offer }: OfferAppPreviewProps): JSX.Element => {
  const { venue } = offer
  const image = getIndividualOfferImage(offer)

  const cropPreviewText = (text: string, maxLength = 300): string => {
    if (text.trim().length > maxLength) {
      return `${text.slice(0, maxLength)}...`
    }
    return text
  }

  return (
    <div className={style['offer-preview-container']}>
      <div className={style['offer-img-container']}>
        {image ? (
          <img
            className={style['offer-img']}
            src={image.url}
            alt="Image de l’offre"
          />
        ) : (
          <p>Pas d’image</p>
        )}
      </div>

      <div className={style['offer-data-container']}>
        {offer.name && (
          <h2 className={style['offer-title']}>
            {cropPreviewText(offer.name, 90)}
          </h2>
        )}

        <OptionsIcons
          className={style['offer-options']}
          isEvent={offer.isEvent}
          isDuo={offer.isDuo}
        />

        {offer.description && (
          <div className={style['offer-description']}>
            {cropPreviewText(offer.description)}
          </div>
        )}

        {!venue.isVirtual && (
          <VenueDetails
            venue={venue}
            withdrawalDetails={
              offer.withdrawalDetails
                ? cropPreviewText(offer.withdrawalDetails)
                : undefined
            }
          />
        )}
      </div>
    </div>
  )
}

export default OfferAppPreview
