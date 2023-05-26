import { captureException } from '@sentry/react'
import isEqual from 'lodash/isEqual'
import React, { memo, useContext, useEffect, useState } from 'react'
import type {
  InfiniteHitsProvided,
  StatsProvided,
} from 'react-instantsearch-core'
import { connectInfiniteHits, connectStats } from 'react-instantsearch-dom'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  AdageFrontRoles,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { getCollectiveOfferAdapter } from 'pages/AdageIframe/app/adapters/getCollectiveOfferAdapter'
import { getCollectiveOfferTemplateAdapter } from 'pages/AdageIframe/app/adapters/getCollectiveOfferTemplateAdapter'
import { AnalyticsContext } from 'pages/AdageIframe/app/providers/AnalyticsContextProvider'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { LOGS_DATA } from 'utils/config'
import { ResultType } from 'utils/types'

import { Spinner } from '../../../Layout/Spinner/Spinner'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import Offer from './Offer'
import styles from './Offers.module.scss'
import { extractOfferIdFromObjectId, offerIsBookable } from './utils'

export interface OffersComponentProps
  extends StatsProvided,
    OffersComponentPropsWithHits {}

interface OffersComponentPropsWithHits
  extends InfiniteHitsProvided<ResultType> {
  userRole: AdageFrontRoles
  userEmail?: string | null
  setIsLoading: (isLoading: boolean) => void
  handleResetFiltersAndLaunchSearch?: () => void
  displayStats?: boolean
}

type OfferMap = Map<
  string,
  CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
>

export const OffersComponent = ({
  userRole,
  userEmail,
  setIsLoading,
  handleResetFiltersAndLaunchSearch,
  hits,
  hasMore,
  refineNext,
  nbHits,
  displayStats = true,
}: OffersComponentProps): JSX.Element => {
  const [queriesAreLoading, setQueriesAreLoading] = useState(false)
  const [offers, setOffers] = useState<
    (HydratedCollectiveOffer | HydratedCollectiveOfferTemplate)[]
  >([])
  const [queryId, setQueryId] = useState('')
  const [fetchedOffers, setFetchedOffers] = useState<OfferMap>(new Map())

  const { filtersKeys, hasClickedSearch, setHasClickedSearch } =
    useContext(AnalyticsContext)

  useEffect(() => {
    // wait for nbHits to update before sending data results
    if (LOGS_DATA && hasClickedSearch) {
      apiAdage.logSearchButtonClick({
        filters: filtersKeys,
        resultsCount: nbHits,
      })
      setHasClickedSearch(false)
    }
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
          return
        } catch (e) {
          captureException(e)
          return
        }
      })
    ).then(offersFromHits => {
      const bookableOffers = offersFromHits.filter(
        offer => typeof offer !== 'undefined'
      ) as (HydratedCollectiveOffer | HydratedCollectiveOfferTemplate)[]

      setOffers(bookableOffers)
      setQueriesAreLoading(false)
      setIsLoading(false)
    })
  }, [hits])

  if (queriesAreLoading && offers.length === 0) {
    return (
      <div className={styles['offers-loader']}>
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
      {displayStats && (
        <div className={styles['offers-stats']}>
          {`${nbHits} résultat${nbHits > 1 ? 's' : ''}`}
        </div>
      )}
      <ul className={styles['offers-list']}>
        {offers.map((offer, index) => (
          <div key={`${offer.isTemplate ? 'T' : ''}${offer.id}`}>
            <Offer
              offer={offer}
              position={index}
              queryId={queryId}
              userEmail={userEmail}
              userRole={userRole}
            />
          </div>
        ))}
        <div className={styles['offers-load-more']}>
          <div className={styles['offers-load-more-text']}>
            {hasMore
              ? `Vous avez vu ${offers.length} offre${
                  offers.length > 1 ? 's' : ''
                } sur ${nbHits}`
              : 'Vous avez vu toutes les offres qui correspondent à votre recherche.'}
          </div>
          {hasMore &&
            (queriesAreLoading ? (
              <div className={styles['offers-loader']}>
                <Spinner message="Chargement en cours" />
              </div>
            ) : (
              <Button onClick={refineNext} variant={ButtonVariant.SECONDARY}>
                Voir plus d’offres
              </Button>
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
          !isEqual(
            prevProps[prop as keyof OffersComponentProps],
            nextProps[prop as keyof OffersComponentProps]
          ) &&
          // add this condition to fix multiple renders when nbHits and hits.length doesn't match
          (nextProps['nbHits'] === nextProps['hits'].length ||
            (nextProps['nbHits'] > nextProps['hits'].length &&
              nextProps['hasMore']))
        ) {
          arePropsEqual = false
        }
      })
      if (arePropsEqual) {
        nextProps.setIsLoading(false)
      }
      return arePropsEqual
    })
  )
)
