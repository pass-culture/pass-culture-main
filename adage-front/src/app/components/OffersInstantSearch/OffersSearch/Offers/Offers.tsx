import './Offers.scss'
import { captureException } from '@sentry/react'
import React, { useEffect, useState } from 'react'
import type { InfiniteHitsProvided } from 'react-instantsearch-core'
import { connectInfiniteHits, Stats } from 'react-instantsearch-dom'
import { useQueries } from 'react-query'

import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'api/gen'
import { getCollectiveOfferAdapter } from 'app/adapters/getCollectiveOfferAdapter'
import { getCollectiveOfferTemplateAdapter } from 'app/adapters/getCollectiveOfferTemplateAdapter'
import { Spinner } from 'app/components/Layout/Spinner/Spinner'
import { Button } from 'app/ui-kit'
import { ResultType } from 'utils/types'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import { Offer } from './Offer'

const offerIsBookable = (
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
): boolean => !offer.isSoldOut && !offer.isExpired

const extractOfferIdFromObjectId = (offerId: string): number => {
  const splitResult = offerId.split('T-')

  if (splitResult.length === 2) {
    return Number(splitResult[1])
  }

  return Number(offerId)
}

export interface OffersComponentProps extends InfiniteHitsProvided<ResultType> {
  userRole: AdageFrontRoles
  setIsLoading: (isLoading: boolean) => void
  handleResetFiltersAndLaunchSearch: () => void
}

export const OffersComponent = ({
  userRole,
  setIsLoading,
  handleResetFiltersAndLaunchSearch,
  hits,
  hasMore,
  refineNext,
}: OffersComponentProps): JSX.Element => {
  const [isFirstRender, setIsFirstRender] = useState(true)
  const [queriesAreLoading, setQueriesAreLoading] = useState(false)

  const queries = useQueries(
    hits.map(hit => ({
      queryKey: ['offer', hit.objectID],
      queryFn: async () => {
        try {
          const offerId = extractOfferIdFromObjectId(hit.objectID)
          const { isOk, payload: offer } = await (hit.isTemplate
            ? getCollectiveOfferTemplateAdapter(offerId)
            : getCollectiveOfferAdapter(offerId))

          if (!isOk) {
            return
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
    if (queries.length && queries.every(query => !query.isLoading)) {
      setIsLoading(false)
      setIsFirstRender(false)
    }
  }, [queries, setIsLoading])

  useEffect(() => {
    setQueriesAreLoading(queries.some(query => query.isLoading))
  }, [queries])

  if (
    isFirstRender &&
    (!queries.length || queries.some(query => query.isLoading))
  ) {
    return (
      <div className="offers-loader">
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  const offers = queries
    .map(({ data }) => data)
    .filter(offer => typeof offer !== 'undefined') as (
    | CollectiveOfferResponseModel
    | CollectiveOfferTemplateResponseModel
  )[]

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
        <div className="offers-load-more">
          <div className="offers-load-more-text">
            <Stats
              translations={{
                stats(nbHits: number) {
                  return `Vous avez vu ${offers.length} offre${
                    offers.length > 1 ? 's' : ''
                  } sur ${nbHits}`
                },
              }}
            />
          </div>
          {hasMore &&
            (queriesAreLoading ? (
              <div className="offers-loader">
                <Spinner message="Chargement en cours" />
              </div>
            ) : (
              <Button
                label="Voir plus d’offres"
                onClick={refineNext}
                type="button"
                variant="secondary"
              />
            ))}
        </div>
      </ul>
    </>
  )
}

export const Offers = connectInfiniteHits<OffersComponentProps, ResultType>(
  OffersComponent
)
