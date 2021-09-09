import "./Offer.scss"
import React, { Fragment, useEffect, useState } from "react"

import * as pcapi from "repository/pcapi/pcapi"
import { ASSETS_URL } from "utils/config"
import { OfferType, ResultType } from "utils/types"

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

  const { address, city, name, postalCode, publicName } = offer?.venue || {}

  return (
    <div className="offer-container">
      {hasThumb && (
        <img
          alt="Offer thumb"
          className="offer-image"
          height="300"
          loading="lazy"
          src={`${ASSETS_URL}${result.thumb_url?.raw}`}
          width="200"
        />
      )}
      {!hasThumb && (
        <img
          alt="placeholder"
          className="offer-image"
          height="300"
          loading="lazy"
          src="/icons/placeholder.svg"
          width="200"
        />
      )}
      <div>
        <div>
          <p>
            {result.name.raw}
          </p>
          <p>
            {result.venue_public_name?.raw ||
              formatToReadableString(result.venue_name?.raw)}
          </p>
        </div>
        <span>
          <p>
            Quoi ?
          </p>
          <p>
            Théâtre
          </p>
        </span>
        <div>
          <p>
            Et en détails ? :
          </p>
          <p>
            Le soleil me rencontre....
          </p>
        </div>
        <div>
          <p>
            Où ?
          </p>
          <address>
            {publicName || name}
            <br />
            {address && (
              <Fragment>
                {address}
                <br />
              </Fragment>
            )}
            {postalCode && (
              <Fragment>
                {postalCode}
                <br />
              </Fragment>
            )}
            {city && (
              <Fragment>
                {city}
                <br />
              </Fragment>
            )}
          </address>
        </div>
      </div>
    </div>
  )
}

export default Offer
