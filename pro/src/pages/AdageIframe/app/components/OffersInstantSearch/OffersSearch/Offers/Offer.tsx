import './Offer.scss'

import cn from 'classnames'
import React, { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import { useActiveFeature } from 'pages/AdageIframe/app/hooks/useActiveFeature'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
  isCollectiveOffer,
} from 'pages/AdageIframe/app/types/offers'
import { ModalLayout } from 'pages/AdageIframe/app/ui-kit'
import { ReactComponent as ChevronIcon } from 'pages/AdageIframe/assets/chevron.svg'
import { ReactComponent as LikeIcon } from 'pages/AdageIframe/assets/like.svg'
import { ReactComponent as LikedIcon } from 'pages/AdageIframe/assets/liked.svg'
import { ReactComponent as Logo } from 'pages/AdageIframe/assets/logo-without-text.svg'
import { ReactComponent as ImagePlaceholder } from 'pages/AdageIframe/assets/offer-image-placeholder.svg'
import { Tag } from 'ui-kit'
import { LOGS_DATA } from 'utils/config'

import ContactButton from './ContactButton'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export interface OfferProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  canPrebookOffers: boolean
  queryId: string
  position: number
}

const Offer = ({
  offer,
  canPrebookOffers,
  queryId,
  position,
}: OfferProps): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)
  const [isModalLikeOpen, setIsModalLikeOpen] = useState(false)
  const isLikeActive = useActiveFeature('WIP_ENABLE_LIKE_IN_ADAGE')

  const openOfferDetails = (
    offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  ) => {
    if (LOGS_DATA) {
      !offer.isTemplate
        ? apiAdage.logOfferDetailsButtonClick({ stockId: offer.stock.id })
        : apiAdage.logOfferTemplateDetailsButtonClick({ offerId: offer.id })
    }
    setDisplayDetails(!displayDetails)
  }

  const handleLikeClick = () => {
    apiAdage.logFavOfferButtonClick({ offerId: offer.id })
    setIsModalLikeOpen(true)
  }

  const closeLikeModal = () => {
    setIsModalLikeOpen(false)
  }

  return (
    <li className="offer" data-testid="offer-listitem">
      <div
        className={cn('offer-logo-placeholder', {
          'offer-logo-placeholder-showcase': offer.isTemplate,
        })}
        data-testid="thumb-placeholder"
      >
        <Logo />
      </div>
      <div className="offer-main-container">
        <div className="offer-image-container">
          {offer.imageUrl ? (
            <img
              alt=""
              className="offer-image"
              loading="lazy"
              src={offer.imageUrl}
            />
          ) : (
            <div className="offer-image-default">
              <ImagePlaceholder />
            </div>
          )}
        </div>
        <div className="offer-container">
          {offer.isTemplate ? (
            <ContactButton
              className="offer-prebooking-button"
              contactEmail={offer.contactEmail}
              contactPhone={offer.contactPhone}
              offerId={offer.id}
              position={position}
              queryId={queryId}
            />
          ) : (
            <PrebookingButton
              canPrebookOffers={canPrebookOffers}
              className="offer-prebooking-button"
              offerId={offer.id}
              queryId={queryId}
              stock={offer.stock}
            />
          )}
          <div className="offer-header">
            <h2 className="offer-header-title">{offer.name}</h2>
            <div className="offer-header-subtitles">
              <span className="offer-header-label">Proposée par </span>
              <span>{getOfferVenueAndOffererName(offer.venue)}</span>
            </div>
            {isCollectiveOffer(offer) && offer.teacher && (
              <div className="offer-header-subtitles">
                <span className="offer-header-label">Destinée à </span>
                <span>
                  {offer.teacher.firstName} {offer.teacher.lastName}
                </span>
              </div>
            )}
            <ul className="offer-domains-list">
              {offer?.domains?.map(domain => (
                <li className="offer-domains-list-item" key={domain.id}>
                  <Tag label={domain.name} />
                </li>
              ))}
            </ul>
          </div>
          <OfferSummary offer={offer} />
          <p className="offer-description">
            {formatDescription(offer.description)}
          </p>
          <div className="offer-footer">
            <button
              className="offer-see-more"
              onClick={() => openOfferDetails(offer)}
              type="button"
            >
              <ChevronIcon
                className={cn('offer-see-more-icon', {
                  'offer-see-more-icon-closed': !displayDetails,
                })}
              />
              en savoir plus
            </button>
            {isLikeActive && (
              <LikeIcon
                className="offer-like-button"
                onClick={handleLikeClick}
              />
            )}
            <ModalLayout
              Icon={LikedIcon}
              closeModal={closeLikeModal}
              isOpen={isModalLikeOpen}
            >
              <p className="like-modal-text">
                Lʼéquipe du pass Culture a bien noté votre intérêt pour cette
                fonctionnalité. Elle arrivera bientôt !
              </p>
            </ModalLayout>
          </div>

          {displayDetails && <OfferDetails offer={offer} />}
        </div>
      </div>
    </li>
  )
}
export default Offer
