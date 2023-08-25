import cn from 'classnames'
import React, { useState } from 'react'

import { AdageFrontRoles, OfferAddressType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import DialogBox from 'components/DialogBox/DialogBox'
import useActiveFeature from 'hooks/useActiveFeature'
import fullLikeIcon from 'icons/full-like.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeFranceIcon from 'icons/stroke-france.svg'
import strokeLikeIcon from 'icons/stroke-like.svg'
import strokeLocalisationIcon from 'icons/stroke-localisation.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
  isCollectiveOffer,
} from 'pages/AdageIframe/app/types/offers'
import { Button, Tag } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'
import { getDistance } from 'utils/getDistance'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import ContactButton from './ContactButton'
import style from './Offer.module.scss'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export interface OfferProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  queryId: string
  position: number
}

const Offer = ({ offer, queryId, position }: OfferProps): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)
  const [isModalLikeOpen, setIsModalLikeOpen] = useState(false)
  const isLikeActive = useActiveFeature('WIP_ENABLE_LIKE_IN_ADAGE')
  const isGeolocationActive = useActiveFeature('WIP_ENABLE_ADAGE_GEO_LOCATION')
  const adageUser = useAdageUser()

  const openOfferDetails = (
    offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  ) => {
    if (LOGS_DATA) {
      !offer.isTemplate
        ? apiAdage.logOfferDetailsButtonClick({
            iframeFrom: removeParamsFromUrl(location.pathname),
            stockId: offer.stock.id,
            queryId: queryId,
          })
        : apiAdage.logOfferTemplateDetailsButtonClick({
            iframeFrom: removeParamsFromUrl(location.pathname),
            offerId: offer.id,
            queryId: queryId,
          })
    }
    setDisplayDetails(!displayDetails)
  }

  const handleLikeClick = () => {
    apiAdage.logFavOfferButtonClick({
      iframeFrom: removeParamsFromUrl(location.pathname),
      offerId: offer.id,
      queryId: queryId,
    })
    setIsModalLikeOpen(true)
  }

  return (
    <li className={style['offer']} data-testid="offer-listitem">
      {offer.venue.coordinates.latitude &&
        offer.venue.coordinates.longitude &&
        isGeolocationActive && (
          <div className={style['offer-geoloc']}>
            <SvgIcon
              alt=""
              src={strokeLocalisationIcon}
              width="16"
              className={style['offer-geoloc-icon']}
            />
            <div>
              basé à{' '}
              {getDistance(
                {
                  latitude: offer.venue.coordinates.latitude,
                  longitude: offer.venue.coordinates.longitude,
                },
                // TODO: Change to real data when available (waiting for Adage to provide it)
                {
                  latitude: 0,
                  longitude: 0,
                }
              )}{' '}
              km de votre établissement
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
          {offer.isTemplate ? (
            <ContactButton
              className={style['offer-prebooking-button']}
              contactEmail={offer.contactEmail}
              contactPhone={offer.contactPhone}
              offerId={offer.id}
              position={position}
              queryId={queryId}
              userEmail={adageUser.email}
              userRole={adageUser.role}
            />
          ) : (
            <PrebookingButton
              canPrebookOffers={adageUser.role == AdageFrontRoles.REDACTOR}
              className={style['offer-prebooking-button']}
              offerId={offer.id}
              queryId={queryId}
              stock={offer.stock}
            />
          )}
          <div className={style['offer-header']}>
            <h2 className={style['offer-header-title']}>{offer.name}</h2>
            <div className={style['offer-header-subtitles']}>
              <span className={style['offer-header-label']}>Proposée par </span>
              <span>{getOfferVenueAndOffererName(offer.venue)}</span>
            </div>

            {isCollectiveOffer(offer) && offer.teacher && (
              <div className={style['offer-header-subtitles']}>
                <span className={style['offer-header-label']}>Destinée à </span>
                <span>
                  {offer.teacher.firstName} {offer.teacher.lastName}
                </span>
              </div>
            )}
            <ul className={style['offer-domains-list']}>
              {offer?.domains?.map(domain => (
                <li
                  className={style['offer-domains-list-item']}
                  key={domain.id}
                >
                  <Tag
                    label={domain.name}
                    className={style['offer-domains-tag']}
                  />
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
            {isLikeActive && (
              <Button
                icon={strokeLikeIcon}
                className={style['offer-like-button']}
                title="bouton j'aime"
                variant={ButtonVariant.TERNARY}
                onClick={handleLikeClick}
              />
            )}
            {isModalLikeOpen && (
              <DialogBox
                labelledBy="aimer une offre"
                extraClassNames={style['offer-like-modal']}
                hasCloseButton
              >
                <SvgIcon
                  src={fullLikeIcon}
                  alt=""
                  width="88"
                  className={style['full-like-icon']}
                />
                <p className={style['offer-like-modal-text']}>
                  Lʼéquipe du pass Culture a bien noté votre intérêt pour cette
                  fonctionnalité. Elle arrivera bientôt !
                </p>
                <Button
                  onClick={() => setIsModalLikeOpen(false)}
                  className={style['offer-like-modal-button']}
                >
                  Fermer
                </Button>
              </DialogBox>
            )}
          </div>

          {displayDetails && <OfferDetails offer={offer} />}
        </div>
      </div>
    </li>
  )
}
export default Offer
