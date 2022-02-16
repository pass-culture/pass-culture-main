import './Offer.scss'
import cn from 'classnames'
import React, { useState } from 'react'

import { ReactComponent as ChevronIcon } from 'assets/chevron.svg'
import { ReactComponent as Logo } from 'assets/logo-without-text.svg'
import { OfferType, VenueType } from 'utils/types'

import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'

const formatToReadableString = (input: string | null): string | null => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

const getOfferVenueAndOffererName = (offerVenue: VenueType): string => {
  const venueName =
    offerVenue.publicName || formatToReadableString(offerVenue.name)
  const offererName = offerVenue.managingOfferer.name

  if (venueName?.toLowerCase() === offererName.toLowerCase()) {
    return venueName
  }

  if (!venueName) {
    return offererName
  }

  return `${venueName} - ${offererName}`
}

export const Offer = ({
  offer,
  canPrebookOffers,
}: {
  canPrebookOffers: boolean
  offer: OfferType
}): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)

  return (
    <li className="offer" data-testid="offer-listitem">
      <div
        className={cn('offer-image-placeholder', {
          'offer-image-placeholder-showcase': offer?.extraData?.isShowcase,
        })}
        data-testid="thumb-placeholder"
      >
        <Logo />
      </div>
      <div className="offer-container">
        <PrebookingButton
          canPrebookOffers={canPrebookOffers}
          className="offer-prebooking-button"
          stock={offer.stocks[0]}
          venue={offer.venue}
        />
        <div className="offer-header">
          <h2 className="offer-header-title">{offer.name}</h2>
          <p className="offer-venue-name">
            {getOfferVenueAndOffererName(offer.venue)}
          </p>
        </div>
        <OfferSummary offer={offer} />
        <p className="offer-description">{offer.description}</p>
        <button
          className="offer-see-more"
          onClick={() => setDisplayDetails(!displayDetails)}
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
