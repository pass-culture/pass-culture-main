import { GetIndividualOfferWithAddressResponseModel } from '@/apiClient//v1'
import { getIndividualOfferImage } from '@/components/IndividualOffer/utils/getIndividualOfferImage'
import { Markdown } from '@/components/Markdown/Markdown'

import style from './OfferAppPreview.module.scss'
import { OptionsIcons } from './OptionsIcons/OptionsIcons'
import { VenueDetails } from './VenueDetails/VenueDetails'

interface OfferAppPreviewProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const OfferAppPreview = ({
  offer,
}: OfferAppPreviewProps): JSX.Element => {
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
            <Markdown
              markdownText={offer.description}
              maxLength={200}
              croppedTextEnding={'<b> Afficher plus...</b>'}
            />
          </div>
        )}

        {!offer.isDigital && (
          <VenueDetails
            address={offer.address}
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
