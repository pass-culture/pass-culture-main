import "./Offers.scss"
import React, { useEffect, useState } from "react"

import * as pcapi from "repository/pcapi/pcapi"
import { OfferType, ResultType, Role } from "utils/types"

import { NoResultsPage } from "./NoResultsPage/NoResultsPage"
import { Offer } from "./Offer"

export const Offers = ({
  userRole,
  results,
}: {
  userRole: Role;
  results: ResultType[];
}): JSX.Element => {
  const offersThumbById = {}
  results.forEach(
    (result) =>
      (offersThumbById[parseInt(result.id.raw)] = result.thumb_url?.raw)
  )

  const [offers, setOffers] = useState<OfferType[]>([])

  const offerIsBookable = (offer: OfferType): boolean =>
    !offer.isSoldOut && !offer.isExpired

  useEffect(() => {
    let isSubscribed = true
    const offersFetchPromises = results.map((result) => {
      return pcapi
        .getOffer(result.id.raw)
        .then((offer) => {
          if (offerIsBookable(offer)) {
            return offer
          }
        })
        .catch(() => {
          // Swallow exception
        })
    })

    Promise.all(offersFetchPromises)
      .then((maybeOffers) => maybeOffers.filter((offer) => offer !== undefined))
      .then((offers: OfferType[]) => {
        if (isSubscribed) setOffers(offers)
      })

    return () => {
      isSubscribed = false
    }
  }, [results])

  if (results.length === 0 || offers.length === 0) {
    return <NoResultsPage />
  }

  return (
    <ul className="offers">
      {offers.map((offer) => (
        <Offer
          canPrebookOffers={userRole == Role.redactor}
          key={offer.id}
          offer={offer}
          thumbUrl={offersThumbById[offer.id]}
        />
      ))}
    </ul>
  )
}
