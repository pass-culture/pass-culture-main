import { useEffect, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getFavoriteOffersAdapter } from '../../adapters/getFavoriteOffersAdapter'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersFavorites.module.scss'
import { OffersFavoritesNoResult } from './OffersFavoritesNoResult/OffersFavoritesNoResult'

export const OffersFavorites = () => {
  const [favoriteOffers, setFavoriteOffers] = useState<
    (CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel)[]
  >([])

  const [isLoading, setIsLoading] = useState<boolean>(false)

  useEffect(() => {
    const fetchFavorites = async () => {
      setIsLoading(true)
      return await getFavoriteOffersAdapter().then((response) => {
        setIsLoading(false)

        if (!response.isOk) {
          return
        }
        setFavoriteOffers(response.payload)
      })
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
    return <Spinner message="Chargement en cours" />
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
                <Offer
                  offer={offer}
                  queryId=""
                  position={i}
                  afterFavoriteChange={(isFavorite) => {
                    favoriteChangeHandler(isFavorite, offer.id)
                  }}
                ></Offer>
              </li>
            )
          })}
        </ul>
      )}
    </>
  )
}
