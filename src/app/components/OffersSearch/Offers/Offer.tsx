import "./Offer.scss"
import React, { Fragment, useEffect, useState } from "react"

import { ReactComponent as Logo } from "assets/logo.svg"
import * as pcapi from "repository/pcapi/pcapi"
import { ASSETS_URL } from "utils/config"
import { OfferType, ResultType } from "utils/types"

import Stocks from "./Stocks/Stocks"

export const formatToReadableString = (input: string | null): string | null => {
  if (input == null) {
    return input
  }
  const lowerCasedInput = input.toLowerCase()
  return lowerCasedInput.charAt(0).toUpperCase() + lowerCasedInput.slice(1)
}

export const Offer = ({ result }: { result: ResultType }): JSX.Element => {
  const [offer, setOffer] = useState<OfferType | null>(null)

  const hasThumb = result.thumb_url?.raw != null

  useEffect(() => {
    pcapi.getOffer(result.id.raw).then((offer) => setOffer(offer))
  }, [result.id])

  return (
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
      {offer && (
        <div className="info">
          <h2>
            {result.name.raw}
          </h2>
          <p className="venue-name">
            {result.venue_public_name?.raw ||
              formatToReadableString(result.venue_name?.raw)}
          </p>
          <section>
            <h3>
              Quoi ?
            </h3>
            Théâtre
          </section>
          <section>
            <h3>
              Et en détails ? :
            </h3>
            Le soleil me rencontre....
          </section>
          <section>
            <h3>
              Quand ?
            </h3>
            <Stocks
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
      )}
    </li>
  )
}

export default Offer
