import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  OfferAddressType,
} from 'apiClient/adage'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { isCollectiveOfferBookable } from 'pages/AdageIframe/app/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { OfferFavoriteButton } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import { OfferShareLink } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferShareLink/OfferShareLink'
import { getOfferVenueAndOffererName } from '../../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferVenueAndOffererName'
import {
  getLocation,
  getLocationForOfferVenue,
} from '../AdageOfferDetailsSection/AdageOfferInfoSection'
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
}: AdageOfferHeaderProps) {
  const isOfferBookable = isCollectiveOfferBookable(offer)

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  const studentLevels =
    offer.students.length > 1 ? 'Multiniveaux' : offer.students[0]

  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const location = isCollectiveOaActive
    ? offer.location
      ? getLocation(offer.location, true)
      : 'Localisation à définir'
    : getLocationForOfferVenue(offer.offerVenue)

  let offerVenueLabel = `${offer.venue.postalCode}, ${offer.venue.city}`
  if (offer.offerVenue.addressType === OfferAddressType.OTHER) {
    offerVenueLabel = offer.offerVenue.otherAddress
  } else if (offer.offerVenue.addressType === OfferAddressType.SCHOOL) {
    offerVenueLabel = 'Dans l’établissement scolaire'
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
                  className={styles['offer-header-action']}
                  queryId={''}
                  playlistId={playlistId}
                />
              )}
              <OfferShareLink
                className={styles['offer-header-action']}
                offer={offer}
              />
            </div>
          )}
        </div>
        <div className={styles['offer-header-details-structure']}>
          Proposée par {venueAndOffererName}
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
            <span>{isCollectiveOaActive ? location : offerVenueLabel}</span>
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
