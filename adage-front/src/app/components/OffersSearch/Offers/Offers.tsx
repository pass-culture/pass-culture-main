import './Offers.scss'
import { captureException } from '@sentry/react'
import React, { useEffect } from 'react'
import { connectHits } from 'react-instantsearch-core'
import { Stats } from 'react-instantsearch-dom'
import { useQueries } from 'react-query'

import { Spinner } from 'app/components/Layout/Spinner/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import { isNewOfferDesignEnabled } from 'utils/isNewOfferDesignEnabled'
import { OfferType, ResultType, Role } from 'utils/types'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import { Offer } from './Offer'
import { OfferLegacy } from './OfferLegacy'

const offerIsBookable = (offer: OfferType): boolean =>
  !offer.isSoldOut && !offer.isExpired

export const OffersComponent = ({
  userRole,
  setIsLoading,
  hits,
}: {
  userRole: Role
  setIsLoading: (isLoading: boolean) => void
  hits: ResultType[]
}): JSX.Element => {
  const offersThumbById = {}
  hits.forEach(hit => {
    offersThumbById[hit.objectID] = hit.offer.thumbUrl
  })

  const queries = useQueries(
    hits.map(hit => ({
      queryKey: ['offer', hit.objectID],
      queryFn: async () => {
        try {
          const offer = await pcapi.getOffer(hit.objectID)
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
    return <NoResultsPage />
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
            {isNewOfferDesignEnabled() ? (
              <Offer
                canPrebookOffers={userRole == Role.redactor}
                key={offer.id}
                offer={offer}
              />
            ) : (
              <OfferLegacy
                canPrebookOffers={userRole == Role.redactor}
                key={offer.id}
                offer={offer}
                thumbUrl={offersThumbById[offer.id]}
              />
            )}
          </div>
        ))}
      </ul>
    </>
  )
}

export const Offers = connectHits(OffersComponent)
