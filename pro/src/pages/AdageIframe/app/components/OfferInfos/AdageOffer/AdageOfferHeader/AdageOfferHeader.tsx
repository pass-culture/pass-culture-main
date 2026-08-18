import cn from 'classnames'
import { useId } from 'react'

import {
  AdageFrontRoles,
  type AuthenticatedResponse,
  type CollectiveOfferResponseModel,
  type CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import strokeCalendarIcon from '@/icons/stroke-calendar.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeLocationIcon from '@/icons/stroke-location.svg'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { isCollectiveOfferBookable } from '@/pages/AdageIframe/app/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { OfferFavoriteButton } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import { OfferShareLink } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferShareLink/OfferShareLink'
import { getOfferVenueAndOffererName } from '../../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferVenueAndOffererName'
import { getLocation } from '../AdageOfferDetailsSection/AdageOfferInfoSection'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '../utils/adageOfferDates'
import { getBookableOfferInstitutionAndTeacherName } from '../utils/adageOfferInstitution'
import { getBookableOfferStockPrice } from '../utils/adageOfferStocks'
import styles from './AdageOfferHeader.module.scss'

export type AdageOfferHeaderProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  adageUser?: AuthenticatedResponse
  isPreview?: boolean
  playlistId?: number
}

export function AdageOfferHeader({
  offer,
  adageUser,
  isPreview,
  playlistId,
}: Readonly<AdageOfferHeaderProps>) {
  const isOfferBookable = isCollectiveOfferBookable(offer)
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )
  const imageCreditId = useId()

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  const studentLevels =
    offer.students.length > 1 ? 'Multiniveaux' : offer.students[0]

  const location = offer.location
    ? getLocation(offer.location, true)
    : 'Localisation à définir'

  return (
    <>
      <div className={styles['offer-header-image-container']}>
        {offer.imageUrl ? (
          <figure>
            <img
              alt=""
              className={styles['offer-header-image']}
              loading="lazy"
              src={offer.imageUrl}
              aria-describedby={offer.imageCredit ? imageCreditId : undefined}
            />
            {offer.imageCredit ? (
              <figcaption id={imageCreditId}>
                <p className={styles['offer-header-image-credit-text']}>
                  Crédit image : {offer.imageCredit}
                </p>
              </figcaption>
            ) : null}
          </figure>
        ) : (
          <div className={styles['offer-header-image-fallback']}>
            <SvgIcon src={strokeOfferIcon} alt="" width="80" />
          </div>
        )}
      </div>
      <div className={styles['offer-header-details']}>
        <div className={styles['offer-header-title-container']}>
          {isPreview ? (
            <h2 className={styles['offer-header-title']}>{offer.name}</h2>
          ) : (
            <h1 className={styles['offer-header-title']}>{offer.name}</h1>
          )}

          {!isPreview && offer.isTemplate && (
            <div className={styles['offer-header-actions']}>
              {adageUser?.role === AdageFrontRoles.REDACTOR && (
                <OfferFavoriteButton
                  offer={offer}
                  queryId={''}
                  playlistId={playlistId}
                />
              )}
              <OfferShareLink offer={offer} />
            </div>
          )}
        </div>
        <p className={styles['offer-header-details-structure']}>
          Proposée par {venueAndOffererName}
        </p>
        {isOfferBookable && offer.educationalInstitution && (
          <div className={styles['offer-header-details-institution']}>
            <p className={styles['offer-header-details-institution-text']}>
              Adressée à{' '}
            </p>
            <p
              className={cn(
                styles['offer-header-details-institution-text'],
                styles['offer-header-details-institution-name']
              )}
            >
              {getBookableOfferInstitutionAndTeacherName(offer)}
            </p>
          </div>
        )}
        <ul className={styles['offer-header-details-infos']}>
          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeLocationIcon} alt="" width="16" />
            <p className={styles['offer-header-details-info-text']}>
              {location}
            </p>
          </li>

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeCalendarIcon} alt="" width="16" />
            <p className={styles['offer-header-details-info-text']}>
              {isOfferBookable
                ? getFormattedDatesForBookableOffer(offer)
                : getFormattedDatesForTemplateOffer(offer)}
            </p>
          </li>

          {isOfferBookable && (
            <li className={styles['offer-header-details-info']}>
              <SvgIcon src={strokeEuroIcon} alt="" width="16" />
              <p className={styles['offer-header-details-info-text']}>
                {getBookableOfferStockPrice(offer, isNewCollectivePriceEnabled)}
              </p>
            </li>
          )}

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeUserIcon} alt="" width="16" />
            <p className={styles['offer-header-details-info-text']}>
              {studentLevels}
            </p>
          </li>
        </ul>
      </div>
    </>
  )
}
