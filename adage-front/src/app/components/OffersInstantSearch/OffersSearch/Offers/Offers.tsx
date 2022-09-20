import './Offers.scss'
import { captureException } from '@sentry/react'
import isEqual from 'lodash/isEqual'
import React, { memo, useContext, useEffect, useState } from 'react'
import type {
  InfiniteHitsProvided,
  StatsProvided,
} from 'react-instantsearch-core'
import {
  connectInfiniteHits,
  connectStats,
  Stats,
} from 'react-instantsearch-dom'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient'
import { AdageFrontRoles } from 'apiClient'
import { api } from 'apiClient/api'
import { getCollectiveOfferAdapter } from 'app/adapters/getCollectiveOfferAdapter'
import { getCollectiveOfferTemplateAdapter } from 'app/adapters/getCollectiveOfferTemplateAdapter'
import { Spinner } from 'app/components/Layout/Spinner/Spinner'
import { AnalyticsContext } from 'app/providers/AnalyticsContextProvider'
import { Button } from 'app/ui-kit'
import { LOGS_DATA } from 'utils/config'
import { ResultType } from 'utils/types'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import { Offer } from './Offer'
import { extractOfferIdFromObjectId, offerIsBookable } from './utils'

export interface OffersComponentProps
  extends StatsProvided,
    OffersComponentPropsWithHits {}

interface OffersComponentPropsWithHits
  extends InfiniteHitsProvided<ResultType> {
  userRole: AdageFrontRoles
  setIsLoading: (isLoading: boolean) => void
  handleResetFiltersAndLaunchSearch: () => void
}

type OfferMap = Map<
  string,
  CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
>

export const OffersComponent = ({
  userRole,
  setIsLoading,
  handleResetFiltersAndLaunchSearch,
  hits,
  hasMore,
  refineNext,
  nbHits,
}: OffersComponentProps): JSX.Element => {
  const [queriesAreLoading, setQueriesAreLoading] = useState(false)
  const [offers, setOffers] = useState<
    (CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel)[]
  >([])
  const [queryId, setQueryId] = useState('')
  const [fetchedOffers, setFetchedOffers] = useState<OfferMap>(new Map())

  const { filtersKeys, hasClickedSearch, setHasClickedSearch } =
    useContext(AnalyticsContext)

  useEffect(() => {
    // wait for nbHits to update before sending data results
    if (LOGS_DATA && hasClickedSearch) {
      api.logSearchButtonClick({
        filters: filtersKeys,
        resultsCount: nbHits,
      })
      setHasClickedSearch(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nbHits])

  useEffect(() => {
    setQueriesAreLoading(true)
    if (hits.length != 0 && queryId != hits[0].__queryID) {
      setQueryId(hits[0].__queryID)
    }

    Promise.all(
      hits.map(async hit => {
        if (fetchedOffers.has(hit.objectID)) {
          return Promise.resolve(fetchedOffers.get(hit.objectID))
        }
        try {
          const offerId = extractOfferIdFromObjectId(hit.objectID)
          const { isOk, payload: offer } = await (hit.isTemplate
            ? getCollectiveOfferTemplateAdapter(offerId)
            : getCollectiveOfferAdapter(offerId))

          if (!isOk) {
            return
          }

          if (offer && offerIsBookable(offer)) {
            setFetchedOffers(
              fetchedOffers => new Map(fetchedOffers.set(hit.objectID, offer))
            )

            return offer
          }
        } catch (e) {
          captureException(e)
        }
      })
    ).then(offersFromHits => {
      const bookableOffers = offersFromHits.filter(
        offer => typeof offer !== 'undefined'
      ) as (
        | CollectiveOfferResponseModel
        | CollectiveOfferTemplateResponseModel
      )[]

      setOffers(bookableOffers)
      setQueriesAreLoading(false)
      setIsLoading(false)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hits, setIsLoading])

  if (queriesAreLoading && offers.length === 0) {
    return (
      <div className="offers-loader">
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  if (hits?.length === 0 || offers.length === 0) {
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
        {offers.map((offer, index) => (
          <div key={offer.id}>
            <Offer
              canPrebookOffers={userRole == AdageFrontRoles.REDACTOR}
              key={offer.id}
              offer={offer}
              position={index}
              queryId={queryId}
            />
          </div>
        ))}
        <div className="offers-load-more">
          <div className="offers-load-more-text">
            {hasMore ? (
              <Stats
                translations={{
                  stats(nbHits: number) {
                    return `Vous avez vu ${offers.length} offre${
                      offers.length > 1 ? 's' : ''
                    } sur ${nbHits}`
                  },
                }}
              />
            ) : (
              'Vous avez vu toutes les offres qui correspondent à votre recherche.'
            )}
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

export const Offers = connectInfiniteHits<
  OffersComponentPropsWithHits,
  ResultType
>(
  connectStats<OffersComponentProps>(
    memo(OffersComponent, (prevProps, nextProps) => {
      // prevent OffersComponent from rerendering if props are equal by value
      // and thus trigger fetch multiple times
      let arePropsEqual = true
      Object.keys(prevProps).forEach(prop => {
        if (
          prop !== 'refineNext' &&
          prop !== 'refinePrevious' &&
          !isEqual(prevProps[prop], nextProps[prop])
        ) {
          arePropsEqual = false
        }
      })

      return arePropsEqual
    })
  )
)
