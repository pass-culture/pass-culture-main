import "./Offers.scss"
import React, { useEffect, useMemo, useState } from "react"

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
  const offersThumbById = useMemo(() => {
    const offersThumbById = {}
    results.forEach(
      (result) =>
        (offersThumbById[parseInt(result.id.raw)] = result.thumb_url?.raw)
    )
    return offersThumbById
  }, [results])

  const [offers, setOffers] = useState<OfferType[]>([])

  const offerIsBookable = (offer: OfferType): boolean =>
    !offer.isSoldOut && !offer.isExpired

  useEffect(() => {
    results.forEach((result) => {
      pcapi
        .getOffer(result.id.raw)
        .then((offer) => {
          if (offerIsBookable(offer)) {
            setOffers((currentOffers) => [...currentOffers, offer])
          }
        })
        .catch(() => {
          // Swallow exception
        })
    })
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
