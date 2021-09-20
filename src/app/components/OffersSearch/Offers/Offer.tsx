import "./Offer.scss"
import React, { Fragment, useEffect, useState } from "react"

import { ReactComponent as Logo } from "assets/logo-with-text.svg"
import * as pcapi from "repository/pcapi/pcapi"
import { ASSETS_URL } from "utils/config"
import { OfferType, ResultType } from "utils/types"

import { Stocks } from "./Stocks/Stocks"

export const formatToReadableString = (input: string | null): string | null => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

export const Offer = ({
  canPrebookOffers,
  result,
}: {
  canPrebookOffers: boolean;
  result: ResultType;
}): JSX.Element | null => {
  const [offer, setOffer] = useState<OfferType | null>(null)

  const hasThumb = result.thumb_url?.raw != null
  const offerIsBookable = (offer: OfferType): boolean =>
    !offer.isSoldOut && !offer.isExpired

  useEffect(() => {
    pcapi.getOffer(result.id.raw).then((offer) => {
      if (offerIsBookable(offer)) {
        setOffer(offer)
      }
    })
  }, [result.id])

  return (
    offer && (
      <li className="offer">
        {hasThumb && (
          <img
            alt="Illustration de l'offre"
            loading="lazy"
            src={`${ASSETS_URL}${result.thumb_url?.raw}`}
          />
        )}
        {!hasThumb && (
          <div className="image-placeholder">
            <Logo />
          </div>
        )}
        <div className="info">
          <h2>
            {offer.name}
          </h2>
          <p className="venue-name">
            {offer.venue.publicName || formatToReadableString(offer.venue.name)}
          </p>
          <section>
            <h3>
              Quoi ?
            </h3>
            {offer.category.label}
          </section>
          <section>
            <h3>
              Et en détails ? :
            </h3>
            {offer.description}
          </section>
          <section>
            <h3>
              Quand ?
            </h3>
            <Stocks
              canPrebookOffers={canPrebookOffers}
              stocks={offer.stocks}
              venuePostalCode={offer.venue.postalCode}
            />
          </section>
          <section>
            <h3>
              Où ?
            </h3>
            <address>
              {offer.venue.publicName || name}
              <br />
              {offer.venue.address && (
                <Fragment>
                  {offer.venue.address}
                  <br />
                </Fragment>
              )}
              {offer.venue.postalCode && (
                <Fragment>
                  {offer.venue.postalCode}
                  <br />
                </Fragment>
              )}
              {offer.venue.city && (
                <Fragment>
                  {offer.venue.city}
                  <br />
                </Fragment>
              )}
            </address>
          </section>
        </div>
      </li>
    )
  )
}
