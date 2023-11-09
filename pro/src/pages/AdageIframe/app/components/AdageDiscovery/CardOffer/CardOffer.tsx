import React from 'react'

import {
  CollectiveOfferOfferVenue,
  CollectiveOfferResponseModel,
  OfferVenueResponse,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import logoSchoolTrip from './assets/icon-school-trip.svg'
import logoSchool from './assets/icon-school.svg'
import styles from './CardOffer.module.scss'

// FIX ME : temp type will be replace by api model when available
export interface CardOfferModel extends CollectiveOfferResponseModel {
  venue: OfferVenueResponse & {
    distance: number
  }
  offerVenue: CollectiveOfferOfferVenue & {
    distance: number
  }
  isTemplate: boolean
}

export interface CardComponentProps {
  offer: CardOfferModel
}

const CardOfferComponent = ({ offer }: CardComponentProps) => {
  const tagInfos = {
    [OfferAddressType.SCHOOL]: [{ logo: logoSchool, text: 'En classe' }],
    [OfferAddressType.OFFERER_VENUE]: [
      { logo: logoSchoolTrip, text: 'Sortie' },
      { text: `À ${offer.offerVenue.distance} km` },
    ],
    [OfferAddressType.OTHER]: [
      { logo: logoSchoolTrip, text: 'Sortie' },
      { text: 'Lieu à définir' },
    ],
  }

  return (
    <div className={styles.container}>
      {offer.imageUrl ? (
        <img
          alt=""
          className={styles['offer-image']}
          loading="lazy"
          src={offer.imageUrl}
        />
      ) : (
        <div className={styles['offer-image']}>
          <SvgIcon src={strokeOfferIcon} alt="" />
        </div>
      )}

      <div className={styles['offer-tag-container']}>
        <Tag variant={TagVariant.LIGHT_GREY} className={styles['offer-tag']}>
          <img
            alt=""
            src={tagInfos[offer.offerVenue.addressType][0].logo}
            className={styles['offer-tag-image']}
          />
          <span>{tagInfos[offer.offerVenue.addressType][0].text}</span>
        </Tag>
        {tagInfos[offer.offerVenue.addressType].length > 1 && (
          <Tag variant={TagVariant.LIGHT_GREY} className={styles['offer-tag']}>
            <span>{tagInfos[offer.offerVenue.addressType][1].text}</span>
          </Tag>
        )}
      </div>

      <div className={styles['offer-name']} title={offer.name}>
        {offer.name}
      </div>

      <div className="offer-venue">
        <div className={styles['offer-venue-name']}>{offer.venue.name}</div>
        <div
          className={styles['offer-venue-distance']}
        >{`à ${offer.venue.distance} km - ${offer.venue.city}`}</div>
      </div>
    </div>
  )
}

export default CardOfferComponent
