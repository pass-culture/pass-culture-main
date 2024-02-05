import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
  AdageFrontRoles,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { isCollectiveOfferTemplate } from 'core/OfferEducational'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { HydratedCollectiveOfferTemplate } from 'pages/AdageIframe/app/types/offers'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getRangeToFrenchText, toDateStrippedOfTimezone } from 'utils/date'

import OfferFavoriteButton from '../../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import OfferShareLink from '../../../OffersInstantSearch/OffersSearch/Offers/OfferShareLink/OfferShareLink'
import { getOfferVenueAndOffererName } from '../../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferVenueAndOffererName'

import styles from './AdageOfferHeader.module.scss'

type AdageOfferProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

export default function AdageOfferHeader({ offer }: AdageOfferProps) {
  const { adageUser } = useAdageUser()

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  const formattedDates =
    isCollectiveOfferTemplate(offer) &&
    ((offer.dates?.start &&
      offer.dates?.end &&
      getRangeToFrenchText(
        toDateStrippedOfTimezone(offer.dates.start),
        toDateStrippedOfTimezone(offer.dates.end)
      )) ||
      'Tout au long de l’année scolaire (l’offre est permanente)')

  const studentLevels = offer.students.join(', ')

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
        <ul className={styles['offer-header-details-infos']}>
          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeLocationIcon} alt="" width="16" />
            <span>{offerVenueLabel}</span>
          </li>

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeCalendarIcon} alt="" width="16" />
            <span>{formattedDates}</span>
          </li>

          <li className={styles['offer-header-details-info']}>
            <SvgIcon src={strokeUserIcon} alt="" width="16" />
            <span>{studentLevels}</span>
          </li>
        </ul>
      </div>
    </>
  )
}
