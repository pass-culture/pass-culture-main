import { IVenueDetailsProps, VenueDetails } from './VenueDetails'

import { OptionsIcons } from './OptionsIcons'
import React from 'react'
import style from './OfferAppPreview.module.scss'

interface IOfferPreviewVenueData extends IVenueDetailsProps {
  isVirtual: boolean
}

interface IOfferPreviewOfferData {
  name: string
  description: string
  isEvent: boolean
  isDuo: boolean
}

interface IOfferAppPreview {
  imageSrc?: string
  offerData: IOfferPreviewOfferData
  venueData?: IOfferPreviewVenueData
}

const OfferAppPreview = ({
  imageSrc,
  offerData,
  venueData,
}: IOfferAppPreview): JSX.Element => {
  const cropPreviewText = (text: string): string => {
    const maxLength = 300
    if (text.trim().length > maxLength) {
      return `${text.slice(0, maxLength)}...`
    }
    return text
  }

  return (
    <div className={style['offer-preview-container']}>
      <div className={style['offer-img-container']}>
        {imageSrc ? (
          <img
            className={style['offer-img']}
            src={imageSrc}
            alt="Image de l’offre"
          />
        ) : (
          <p>Pas d'image</p>
        )}
      </div>

      <div className={style['offer-data-container']}>
        {offerData.name && (
          <h2 className={style['offer-title']}>{offerData.name}</h2>
        )}

        <OptionsIcons
          className={style['offer-options']}
          isEvent={offerData.isEvent}
          isDuo={offerData.isDuo}
        />

        {offerData.description && (
          <div className={style['offer-description']}>
            {cropPreviewText(offerData.description)}
          </div>
        )}

        {venueData && !venueData.isVirtual && (
          <VenueDetails
            name={venueData.name}
            publicName={venueData.publicName}
            address={venueData.address}
            postalCode={venueData.postalCode}
            city={venueData.city}
            withdrawalDetails={
              venueData.withdrawalDetails
                ? cropPreviewText(venueData.withdrawalDetails)
                : undefined
            }
          />
        )}
      </div>
    </div>
  )
}

export default OfferAppPreview
