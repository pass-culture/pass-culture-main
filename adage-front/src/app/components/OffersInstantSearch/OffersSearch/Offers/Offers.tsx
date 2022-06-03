import './Offers.scss'
import { captureException } from '@sentry/react'
import React, { useEffect } from 'react'
import type { HitsProvided } from 'react-instantsearch-core'
import { connectHits } from 'react-instantsearch-core'
import { Stats } from 'react-instantsearch-dom'
import { useQueries } from 'react-query'

import { AdageFrontRoles } from 'api/gen'
import { getCollectiveOfferAdapter } from 'app/adapters/getCollectiveOfferAdapter'
import { getCollectiveOfferTemplateAdapter } from 'app/adapters/getCollectiveOfferTemplateAdapter'
import { Spinner } from 'app/components/Layout/Spinner/Spinner'
import { OfferType } from 'app/types/offers'
import * as pcapi from 'repository/pcapi/pcapi'
import { ResultType } from 'utils/types'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import { Offer } from './Offer'

const offerIsBookable = (offer: OfferType): boolean =>
  !offer.isSoldOut && !offer.isExpired

const extractOfferIdFromObjectId = (offerId: string): string => {
  const splitResult = offerId.split('T-')

  if (splitResult.length === 2) {
    return splitResult[1]
  }

  return offerId
}

export interface OffersComponentProps extends HitsProvided<ResultType> {
  userRole: AdageFrontRoles
  setIsLoading: (isLoading: boolean) => void
  handleResetFiltersAndLaunchSearch: () => void
  useNewAlgoliaIndex: boolean
}

export const OffersComponent = ({
  userRole,
  setIsLoading,
  handleResetFiltersAndLaunchSearch,
  hits,
  useNewAlgoliaIndex,
}: OffersComponentProps): JSX.Element => {
  const offersThumbById = {}
  hits.forEach(hit => {
    offersThumbById[hit.objectID] = hit.offer.thumbUrl
  })

  const queries = useQueries(
    hits.map(hit => ({
      queryKey: ['offer', hit.objectID],
      queryFn: async () => {
        try {
          let offer: OfferType
          if (useNewAlgoliaIndex) {
            const offerId = extractOfferIdFromObjectId(hit.objectID)
            const { isOk, payload } = await (hit.isTemplate
              ? getCollectiveOfferTemplateAdapter(offerId)
              : getCollectiveOfferAdapter(offerId))

            if (!isOk) {
              return
            }

            offer = payload as OfferType
          } else {
            offer = await pcapi.getOffer(hit.objectID)
          }
          if (offer && offerIsBookable(offer)) return offer
        } catch (e) {
          captureException(e)
        }
      },
      staleTime: 1 * 60 * 1000, // We consider an offer valid for 1 min
    }))
  )

  useEffect(() => {
    if (queries.every(query => !query.isLoading)) {
      setIsLoading(false)
    }
  }, [queries, setIsLoading])

  if (queries.some(query => query.isLoading)) {
    return (
      <div className="offers-loader">
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  const offers = queries
    .map(({ data }) => data as OfferType | undefined)
    .filter(offer => typeof offer !== 'undefined') as OfferType[]

  if (hits.length === 0 || offers.length === 0) {
    return (
      <NoResultsPage
        handleResetFiltersAndLaunchSearch={handleResetFiltersAndLaunchSearch}
      />
    )
  }

  return (
    <>
      <div className="offers-stats">
        <Stats
          translations={{
            stats(nbHits: number) {
              return `${nbHits} résultat${nbHits > 1 ? 's' : ''}`
            },
          }}
        />
      </div>
      <ul className="offers">
        {offers.map(offer => (
          <div key={offer.id}>
            <Offer
              canPrebookOffers={userRole == AdageFrontRoles.Redactor}
              key={offer.id}
              offer={offer}
            />
          </div>
        ))}
      </ul>
    </>
  )
}

export const Offers = connectHits<OffersComponentProps, ResultType>(
  OffersComponent
)
