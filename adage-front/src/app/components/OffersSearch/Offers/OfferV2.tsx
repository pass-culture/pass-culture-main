import "./OfferV2.scss"
import React from "react"

import { ReactComponent as Logo } from "assets/logo-without-text.svg"
import { OfferType } from "utils/types"

import OfferSummary from "./OfferSummary/OfferSummary"
import PrebookingButton from "./PrebookingButton/PrebookingButton"

const formatToReadableString = (input: string | null): string | null => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

export const Offer = ({
  offer,
  canPrebookOffers
}: {
  canPrebookOffers: boolean;
  offer: OfferType;
}): JSX.Element => {
  return (
    <li className="offer-v2">
      <div
        className="image-placeholder"
        data-testid="thumb-placeholder"
      >
        <Logo />
      </div>
      <div className="offer-container">
        <PrebookingButton
          canPrebookOffers={canPrebookOffers}
          className="offer-prebooking-button"
          stock={offer.stocks[0]}
        />
        <div className="header">
          <h2 className="header-title">
            {offer.name}
          </h2>
          <p className="venue-name">
            {offer.venue.publicName || formatToReadableString(offer.venue.name)}
          </p>
        </div>
        <OfferSummary offer={offer} />
        <p className="description">
          {offer.description}
        </p>
      </div>
    </li>
  )
}
