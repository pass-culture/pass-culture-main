import './Offer.scss'
import React from 'react'

import { ReactComponent as Logo } from 'assets/logo-without-text.svg'
import { OfferType } from 'utils/types'

import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'

const formatToReadableString = (input: string | null): string | null => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

export const Offer = ({
  offer,
  canPrebookOffers,
}: {
  canPrebookOffers: boolean
  offer: OfferType
}): JSX.Element => {
  return (
    <li className="offer">
      <div className="offer-image-placeholder" data-testid="thumb-placeholder">
        <Logo />
      </div>
      <div className="offer-container">
        <PrebookingButton
          canPrebookOffers={canPrebookOffers}
          className="offer-prebooking-button"
          stock={offer.stocks[0]}
        />
        <div className="offer-header">
          <h2 className="offer-header-title">{offer.name}</h2>
          <p className="offer-venue-name">
            {offer.venue.publicName || formatToReadableString(offer.venue.name)}
          </p>
        </div>
        <OfferSummary offer={offer} />
        <p className="offer-description">{offer.description}</p>
      </div>
    </li>
  )
}
