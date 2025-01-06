import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { getIndividualOfferImage } from 'components/IndividualOffer/utils/getIndividualOfferImage'

import style from './OfferAppPreview.module.scss'
import { OptionsIcons } from './OptionsIcons/OptionsIcons'
import { VenueDetails } from './VenueDetails/VenueDetails'

interface OfferAppPreviewProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const OfferAppPreview = ({
  offer,
}: OfferAppPreviewProps): JSX.Element => {
  const { venue } = offer
  const image = getIndividualOfferImage(offer)

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

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
          <div className={style['offer-title']}>
            {cropPreviewText(offer.name, 90)}
          </div>
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
            address={isOfferAddressEnabled ? offer.address : undefined}
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
