import "./Offers.scss"
import { captureException } from "@sentry/react"
import React, { useEffect, useState } from "react"

import { Spinner } from "app/components/Layout/Spinner/Spinner"
import * as pcapi from "repository/pcapi/pcapi"
import { OfferType, ResultType, Role } from "utils/types"

import { NoResultsPage } from "./NoResultsPage/NoResultsPage"
import { Offer } from "./Offer"

const getIdFromResultIdRaw = (resultId: string): number =>
  parseInt(resultId.split("|")[1])

export const Offers = ({
  userRole,
  results,
  isAppSearchLoading,
  wasFirstSearchLaunched,
}: {
  userRole: Role;
  results: ResultType[];
  isAppSearchLoading: boolean;
  wasFirstSearchLaunched: boolean;
}): JSX.Element => {
  const offersThumbById = {}
  results.forEach(
    (result) =>
      (offersThumbById[getIdFromResultIdRaw(result.id.raw)] =
        result.thumb_url?.raw)
  )

  const [offers, setOffers] = useState<OfferType[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const offerIsBookable = (offer: OfferType): boolean =>
    !offer.isSoldOut && !offer.isExpired

  useEffect(() => {
    setIsLoading(true)
    let isSubscribed = true
    const offersFetchPromises = results.map((result) => {
      return pcapi
        .getOffer(getIdFromResultIdRaw(result.id.raw))
        .then((offer) => {
          if (offerIsBookable(offer)) {
            return offer
          }
        })
        .catch((e) => {
          captureException(e)
        })
    })

    Promise.all(offersFetchPromises)
      .then((maybeOffers) => maybeOffers.filter((offer) => offer !== undefined))
      .then((offers: OfferType[]) => {
        if (isSubscribed) {
          setOffers(offers)
          setIsLoading(false)
        }
      })

    return () => {
      isSubscribed = false
    }
  }, [results])

  if (isLoading || isAppSearchLoading || !wasFirstSearchLaunched) {
    return (
      <div className="offers-loader">
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  if (results.length === 0 || offers.length === 0) {
    return <NoResultsPage />
  }

  return (
    <ul className="offers">
      {offers.map((offer, index) => (
        <>
          <Offer
            canPrebookOffers={userRole == Role.redactor}
            key={offer.id}
            offer={offer}
            thumbUrl={offersThumbById[offer.id]}
          />
          {index < offers.length - 1 && <hr className="separator" />}
        </>
      ))}
    </ul>
  )
}
