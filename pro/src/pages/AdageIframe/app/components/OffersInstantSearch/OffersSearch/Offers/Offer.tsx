import cn from 'classnames'
import React, { useState } from 'react'

import { AdageFrontRoles, OfferAddressType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import fullLinkIcon from 'icons/full-link.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeFranceIcon from 'icons/stroke-france.svg'
import strokeLocalisationIcon from 'icons/stroke-localisation.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
  isCollectiveOffer,
} from 'pages/AdageIframe/app/types/offers'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { LOGS_DATA } from 'utils/config'
import { getHumanizeRelativeDistance } from 'utils/getDistance'

import ContactButton from './ContactButton'
import style from './Offer.module.scss'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferFavoriteButton from './OfferFavoriteButton/OfferFavoriteButton'
import OfferShareLink from './OfferShareLink/OfferShareLink'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export interface OfferProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  queryId: string
  position: number
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  openDetails?: boolean
}

const Offer = ({
  offer,
  queryId,
  position,
  afterFavoriteChange,
  isInSuggestions,
  openDetails = false,
}: OfferProps): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(openDetails)
  const { adageUser } = useAdageUser()

  const canAddOfferToFavorites =
    offer.isTemplate && adageUser.role !== AdageFrontRoles.READONLY

  const openOfferDetails = (
    offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  ) => {
    setDisplayDetails(!displayDetails)
    if (!LOGS_DATA) {
      return
    }

    if (!offer.isTemplate) {
      void apiAdage.logOfferDetailsButtonClick({
        iframeFrom: location.pathname,
        stockId: offer.stock.id,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    } else {
      void apiAdage.logOfferTemplateDetailsButtonClick({
        iframeFrom: location.pathname,
        offerId: offer.id,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    }
  }

  function offerVenueLinkClicked() {
    void apiAdage.logTrackingMap({
      iframeFrom: location.pathname,
    })
  }

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  return (
    <div className={style['offer']}>
      {offer.venue.coordinates.latitude &&
        offer.venue.coordinates.longitude &&
        (adageUser.lat || adageUser.lat === 0) &&
        (adageUser.lon || adageUser.lon === 0) && (
          <div className={style['offer-geoloc']}>
            <SvgIcon
              alt=""
              src={strokeLocalisationIcon}
              width="16"
              className={style['offer-geoloc-icon']}
            />
            <div>
              basé à{' '}
              {getHumanizeRelativeDistance(
                {
                  latitude: offer.venue.coordinates.latitude,
                  longitude: offer.venue.coordinates.longitude,
                },
                {
                  latitude: adageUser.lat,
                  longitude: adageUser.lon,
                }
              )}{' '}
              de votre établissement
            </div>
            {offer.offerVenue.addressType !== OfferAddressType.OFFERER_VENUE &&
              adageUser.departmentCode &&
              offer.interventionArea.includes(adageUser.departmentCode) && (
                <>
                  <div className={style['offer-geoloc-separator']} />
                  <SvgIcon
                    alt=""
                    src={strokeFranceIcon}
                    width="16"
                    className={style['offer-geoloc-icon']}
                  />
                  <div>peut se déplacer dans votre département</div>
                </>
              )}
          </div>
        )}
      <div className={style['offer-container']}>
        <div className={style['offer-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={style['offer-image']}
              loading="lazy"
              src={offer.imageUrl}
            />
          ) : (
            <div className={style['offer-image-default']}>
              <SvgIcon src={strokeOfferIcon} alt="" />
            </div>
          )}
        </div>
        <div className={style['offer-details-container']}>
          <div className={style['offer-header']}>
            <div className={style['offer-header-row']}>
              <h2 className={style['offer-header-row-title']}>{offer.name}</h2>
              <div className={style['offer-details-actions']}>
                {canAddOfferToFavorites && (
                  <OfferFavoriteButton
                    offer={offer}
                    afterFavoriteChange={afterFavoriteChange}
                    queryId={queryId}
                  />
                )}
                {offer.isTemplate ? (
                  <>
                    <OfferShareLink offer={offer} />
                    <ContactButton
                      className={style['offer-prebooking-button']}
                      contactEmail={offer.contactEmail}
                      contactPhone={offer.contactPhone}
                      offerId={offer.id}
                      position={position}
                      queryId={queryId}
                      userEmail={adageUser.email}
                      userRole={adageUser.role}
                      isInSuggestions={isInSuggestions}
                    />
                  </>
                ) : (
                  <PrebookingButton
                    canPrebookOffers={
                      adageUser.role == AdageFrontRoles.REDACTOR
                    }
                    className={style['offer-prebooking-button']}
                    offerId={offer.id}
                    queryId={queryId}
                    stock={offer.stock}
                    isInSuggestions={isInSuggestions}
                  />
                )}
              </div>
            </div>

            <div className={style['offer-header-subtitles']}>
              <span className={style['offer-header-label']}>Proposée par</span>

              {offer.venue.adageId ? (
                <ButtonLink
                  link={{
                    isExternal: true,
                    to: `${document.referrer}adage/ressource/partenaires/id/${offer.venue.adageId}`,
                    target: '_blank',
                    rel: 'noopener noreferrer',
                  }}
                  variant={ButtonVariant.TERNARY}
                  className={style['offer-header-venue-link']}
                  onClick={offerVenueLinkClicked}
                  icon={fullLinkIcon}
                >
                  {venueAndOffererName}
                </ButtonLink>
              ) : (
                <span>{venueAndOffererName}</span>
              )}
            </div>
            {isCollectiveOffer(offer) && offer.teacher && (
              <div className={style['offer-header-teacher']}>
                <span className={style['offer-header-label']}>Destinée à </span>
                <span>
                  {offer.teacher.firstName} {offer.teacher.lastName}
                </span>
              </div>
            )}
            <ul className={style['offer-domains-list']}>
              {offer?.domains?.map((domain) => (
                <li
                  className={style['offer-domains-list-item']}
                  key={domain.id}
                >
                  <Tag
                    variant={TagVariant.LIGHT_GREY}
                    className={style['offer-domains-list-item-tag']}
                  >
                    {domain.name}
                  </Tag>
                </li>
              ))}
            </ul>
          </div>
          <OfferSummary offer={offer} />
          <p className={style['offer-description']}>
            {formatDescription(offer.description)}
          </p>
          <div className={style['offer-footer']}>
            <button
              className={style['offer-see-more']}
              onClick={() => openOfferDetails(offer)}
              type="button"
            >
              <SvgIcon
                alt=""
                src={fullUpIcon}
                className={cn(style['offer-see-more-icon'], {
                  [style['offer-see-more-icon-closed']]: !displayDetails,
                })}
                width="16"
              />
              en savoir plus
            </button>
          </div>
          {displayDetails && <OfferDetails offer={offer} />}
        </div>
      </div>
    </div>
  )
}
export default Offer
