import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
  AdageFrontRoles,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { isCollectiveOfferBookable } from 'core/OfferEducational'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { HydratedCollectiveOfferTemplate } from 'pages/AdageIframe/app/types/offers'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import OfferFavoriteButton from '../../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import OfferShareLink from '../../../OffersInstantSearch/OffersSearch/Offers/OfferShareLink/OfferShareLink'
import { getOfferVenueAndOffererName } from '../../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferVenueAndOffererName'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '../utils/adageOfferDates'
import { getBookableOfferInstitutionAndTeacherName } from '../utils/adageOfferInstitution'
import { getBookableOfferStockPrice } from '../utils/adageOfferStocks'

import styles from './AdageOfferHeader.module.scss'

export type AdageOfferProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

export default function AdageOfferHeader({ offer }: AdageOfferProps) {
  const { adageUser } = useAdageUser()
  const isOfferBookable = isCollectiveOfferBookable(offer)

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  const studentLevels =
    offer.students.length > 1 ? 'Multiniveaux' : offer.students[0]

  let offerVenueLabel = `${offer.venue.postalCode}, ${offer.venue.city}`
  if (offer.offerVenue) {
    if (offer.offerVenue.addressType === OfferAddressType.OTHER) {
      offerVenueLabel = offer.offerVenue.otherAddress
    } else if (offer.offerVenue.addressType === OfferAddressType.SCHOOL) {
      offerVenueLabel = 'Dans l’établissement scolaire'
    }
  }

  return (
    <>
      <div className={styles['offer-header-image-container']}>
        {offer.imageUrl ? (
          <img
            alt=""
            className={styles['offer-header-image']}
            loading="lazy"
            src={offer.imageUrl}
          />
        ) : (
          <div className={styles['offer-header-image-fallback']}>
            <SvgIcon src={strokeOfferIcon} alt="" width="80" />
          </div>
        )}
      </div>
      <div className={styles['offer-header-details']}>
        <div className={styles['offer-header-title-container']}>
          <h1 className={styles['offer-header-title']}>{offer.name}</h1>

          {offer.isTemplate && (
            <div className={styles['offer-header-actions']}>
              {/* TODO : Remove the "as". The "as" is temporary while the isTemplate adage rework isn't finished
                Ultimately, HydratedCollectiveOfferTemplate wil be the same model as CollectiveOfferTemplateResponseModel */}
              {adageUser.role === AdageFrontRoles.REDACTOR && (
                <OfferFavoriteButton
                  offer={offer as HydratedCollectiveOfferTemplate}
                  className={styles['offer-header-action']}
                  queryId={''}
                />
              )}
              {/* TODO : Remove the "as". The "as" is temporary while the isTemplate adage rework isn't finished
                Ultimately, HydratedCollectiveOfferTemplate wil be the same model as CollectiveOfferTemplateResponseModel */}
              <OfferShareLink
                className={styles['offer-header-action']}
                tooltipContentClassName={
                  styles['offer-header-share-button-tooltip-content']
                }
                offer={offer as HydratedCollectiveOfferTemplate}
              />
            </div>
          )}
        </div>
        <div className={styles['offer-header-details-structure']}>
          Proposée par{' '}
          <span className={styles['offer-header-details-structure-name']}>
            {venueAndOffererName}
          </span>
        </div>
        {isOfferBookable && offer.educationalInstitution && (
          <div className={styles['offer-header-details-institution']}>
            Adressée à{' '}
            <span className={styles['offer-header-details-institution-name']}>
              {getBookableOfferInstitutionAndTeacherName(offer)}
            </span>
          </div>
        )}
        <ul className={styles['offer-header-details-infos']}>
          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeLocationIcon} alt="" width="16" />
            <span>{offerVenueLabel}</span>
          </li>

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeCalendarIcon} alt="" width="16" />
            <span>
              {isOfferBookable
                ? getFormattedDatesForBookableOffer(offer)
                : getFormattedDatesForTemplateOffer(offer)}
            </span>
          </li>

          {isOfferBookable && (
            <li className={styles['offer-header-details-info']}>
              <SvgIcon src={strokeEuroIcon} alt="" width="16" />
              <span>{getBookableOfferStockPrice(offer)}</span>
            </li>
          )}

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeUserIcon} alt="" width="16" />
            <span>{studentLevels}</span>
          </li>
        </ul>
      </div>
    </>
  )
}
