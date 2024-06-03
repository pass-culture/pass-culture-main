import { useEffect, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useActiveFeature } from 'hooks/useActiveFeature'

import { AdageOfferListCard } from '../OffersInstantSearch/OffersSearch/Offers/AdageOfferListCard/AdageOfferListCard'
import { Offer } from '../OffersInstantSearch/OffersSearch/Offers/Offer'
import { AdageSkeleton } from '../Skeleton/AdageSkeleton'

import styles from './OffersFavorites.module.scss'
import { OffersFavoritesNoResult } from './OffersFavoritesNoResult/OffersFavoritesNoResult'

export const OffersFavorites = () => {
  const [favoriteOffers, setFavoriteOffers] = useState<
    (CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel)[]
  >([])

  const [isLoading, setIsLoading] = useState<boolean>(false)

  const isNewOfferCardEnabled = useActiveFeature(
    'WIP_ENABLE_ADAGE_VISUALIZATION'
  )

  // TODO use SWR
  useEffect(() => {
    const fetchFavorites = async () => {
      setIsLoading(true)
      const offers = (await apiAdage.getCollectiveFavorites()).favoritesTemplate
      setFavoriteOffers(offers)
      setIsLoading(false)
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    fetchFavorites()
  }, [])

  const favoriteChangeHandler = (isFavorite: boolean, id: number) => {
    //  Remove favorite from list after it was removed from favorites
    if (!isFavorite) {
      setFavoriteOffers((prevOffers) =>
        [...prevOffers].filter((offer) => offer.id !== id)
      )
    }
  }

  if (isLoading) {
    return (
      <>
        <AdageSkeleton />
        <AdageSkeleton />
        <AdageSkeleton />
      </>
    )
  }

  return (
    <>
      <h1>Mes Favoris</h1>
      {favoriteOffers.length === 0 ? (
        <OffersFavoritesNoResult />
      ) : (
        <ul className={styles['favorite-list']}>
          {favoriteOffers.map((offer, i) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                {isNewOfferCardEnabled ? (
                  <AdageOfferListCard
                    offer={offer}
                    afterFavoriteChange={(isFavorite) => {
                      favoriteChangeHandler(isFavorite, offer.id)
                    }}
                  />
                ) : (
                  <Offer
                    offer={offer}
                    queryId=""
                    position={i}
                    afterFavoriteChange={(isFavorite) => {
                      favoriteChangeHandler(isFavorite, offer.id)
                    }}
                  />
                )}
              </li>
            )
          })}
        </ul>
      )}
    </>
  )
}
