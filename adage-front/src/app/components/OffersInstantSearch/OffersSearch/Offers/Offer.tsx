import './Offer.scss'
import cn from 'classnames'
import React, { useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient'
import { api } from 'apiClient/api'
import { Tag } from 'app/ui-kit'
import { ReactComponent as ChevronIcon } from 'assets/chevron.svg'
import { ReactComponent as Logo } from 'assets/logo-without-text.svg'
import { LOGS_DATA } from 'utils/config'

import ContactButton from './ContactButton'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'
import { isOfferCollectiveOffer } from './utils/offerIsCollectiveOffer'

export const Offer = ({
  offer,
  canPrebookOffers,
}: {
  canPrebookOffers: boolean
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)
  const offerIsShowcase = !isOfferCollectiveOffer(offer)

  const openOfferDetails = (
    offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  ) => {
    if (LOGS_DATA) {
      isOfferCollectiveOffer(offer)
        ? api.logOfferDetailsButtonClick({ stockId: offer.stock.id })
        : api.logOfferTemplateDetailsButtonClick({ offerId: offer.id })
    }
    setDisplayDetails(!displayDetails)
  }

  return (
    <li className="offer" data-testid="offer-listitem">
      <div
        className={cn('offer-image-placeholder', {
          'offer-image-placeholder-showcase': offerIsShowcase,
        })}
        data-testid="thumb-placeholder"
      >
        <Logo />
      </div>
      <div className="offer-container">
        {offerIsShowcase ? (
          <ContactButton
            className="offer-prebooking-button"
            contactEmail={offer.contactEmail}
            contactPhone={offer.contactPhone}
            offerId={offer.id}
          />
        ) : (
          <PrebookingButton
            canPrebookOffers={canPrebookOffers}
            className="offer-prebooking-button"
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
    </li>
  )
}
