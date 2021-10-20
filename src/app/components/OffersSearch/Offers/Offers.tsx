import "./Offers.scss"
import { captureException } from "@sentry/react"
import React from "react"
import { useQueries } from "react-query"

import { Spinner } from "app/components/Layout/Spinner/Spinner"
import * as pcapi from "repository/pcapi/pcapi"
import { OfferType, ResultType, Role } from "utils/types"

import { NoResultsPage } from "./NoResultsPage/NoResultsPage"
import { Offer } from "./Offer"

const getIdFromResultIdRaw = (resultId: string): number => parseInt(resultId)
const offerIsBookable = (offer: OfferType): boolean =>
  !offer.isSoldOut && !offer.isExpired

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
  results.forEach((result) => {
    const offerId = getIdFromResultIdRaw(result.id.raw)
    offersThumbById[offerId] = result.thumb_url?.raw
  })

  const queries = useQueries(
    results.map((result) => {
      const offerId = getIdFromResultIdRaw(result.id.raw)

      return {
        queryKey: ["offer", offerId],
        queryFn: async () => {
          try {
            const offer = await pcapi.getOffer(offerId)
            if (offer && offerIsBookable(offer)) return offer
          } catch (e) {
            captureException(e)
          }
        },
        staleTime: 1 * 60 * 1000, // We consider an offer valid for 1 min
      }
    })
  )

  const isLoading = queries.some((query) => query.isLoading)
  if (isLoading || isAppSearchLoading || !wasFirstSearchLaunched) {
    return (
      <div className="offers-loader">
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  const offers = queries
    .map(({ data }) => data as OfferType | undefined)
    .filter((offer) => typeof offer !== "undefined") as OfferType[]

  if (results.length === 0 || offers.length === 0) {
    return <NoResultsPage />
  }

  return (
    <ul className="offers">
      {offers.map((offer, index) => (
        <div key={offer.id}>
          <Offer
            canPrebookOffers={userRole == Role.redactor}
            key={offer.id}
            offer={offer}
            thumbUrl={offersThumbById[offer.id]}
          />
          {index < offers.length - 1 && <hr className="separator" />}
        </div>
      ))}
    </ul>
  )
}
