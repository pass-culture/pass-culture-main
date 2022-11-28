import './Offer.scss'
import cn from 'classnames'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { useActiveFeature } from 'app/hooks/useActiveFeature'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'app/types/offers'
import { Tag } from 'app/ui-kit'
import { ReactComponent as ChevronIcon } from 'assets/chevron.svg'
import { ReactComponent as Logo } from 'assets/logo-without-text.svg'
import { ReactComponent as ImagePlaceholder } from 'assets/offer-image-placeholder.svg'
import { LOGS_DATA } from 'utils/config'

import ContactButton from './ContactButton'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export const Offer = ({
  offer,
  canPrebookOffers,
  queryId,
  position,
}: {
  canPrebookOffers: boolean
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  queryId: string
  position: number
}): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)

  const openOfferDetails = (
    offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  ) => {
    if (LOGS_DATA) {
      !offer.isTemplate
        ? api.logOfferDetailsButtonClick({ stockId: offer.stock.id })
        : api.logOfferTemplateDetailsButtonClick({ offerId: offer.id })
    }
    setDisplayDetails(!displayDetails)
  }

  const isCollectiveImageOfferActive = useActiveFeature(
    'WIP_IMAGE_COLLECTIVE_OFFER'
  )

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
        {isCollectiveImageOfferActive && (
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
        )}
        <div
          className="offer-container"
          style={!isCollectiveImageOfferActive ? { paddingLeft: '18px' } : {}}
        >
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
            <p className="offer-venue-name">
              {getOfferVenueAndOffererName(offer.venue)}
            </p>
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
          {displayDetails && <OfferDetails offer={offer} />}
        </div>
      </div>
    </li>
  )
}
