import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { truncateAtWord } from '@/commons/utils/string'
import { Markdown } from '@/components/Markdown/Markdown'

import style from './OfferAppPreview.module.scss'
import { OptionsIcons } from './OptionsIcons/OptionsIcons'
import { VenueDetails } from './VenueDetails/VenueDetails'

interface OfferAppPreviewProps {
  offer: GetIndividualOfferResponseModelV2
}

export const OfferAppPreview = ({
  offer,
}: OfferAppPreviewProps): JSX.Element => {
  const image = getIndividualOfferImage(offer)

  return (
    <div className={style['offer-preview-container']}>
      <div className={style['offer-img-container']}>
        {image ? (
          <img
            className={style['offer-img']}
            src={image.url}
            alt="Illustration de l’offre"
          />
        ) : (
          <p>Pas d’image</p>
        )}
      </div>

      <div className={style['offer-data-container']}>
        {offer.name && (
          <div className={style['offer-title']}>
            {truncateAtWord(offer.name, 90)}
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
            address={offer.location}
            withdrawalDetails={
              offer.withdrawalDetails
                ? truncateAtWord(offer.withdrawalDetails, 300)
                : undefined
            }
          />
        )}
      </div>
    </div>
  )
}
