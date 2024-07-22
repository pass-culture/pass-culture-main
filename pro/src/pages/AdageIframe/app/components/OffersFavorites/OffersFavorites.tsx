import useSWR, { useSWRConfig } from 'swr'

import { apiAdage } from 'apiClient/api'
import { GET_COLLECTIVE_FAVORITES } from 'config/swrQueryKeys'

import { AdageOfferListCard } from '../OffersInstantSearch/OffersSearch/Offers/AdageOfferListCard/AdageOfferListCard'
import { AdageSkeleton } from '../Skeleton/AdageSkeleton'

import styles from './OffersFavorites.module.scss'
import { OffersFavoritesNoResult } from './OffersFavoritesNoResult/OffersFavoritesNoResult'

export const OffersFavorites = () => {
  const { data: offers, isLoading } = useSWR(
    [GET_COLLECTIVE_FAVORITES],
    () => apiAdage.getCollectiveFavorites(),
    { fallbackData: { favoritesTemplate: [], favoritesOffer: [] } }
  )
  const { mutate } = useSWRConfig()

  const favoriteChangeHandler = async (isFavorite: boolean, id: number) => {
    if (!isFavorite) {
      const newFavoriteOffers = {
        favoritesTemplate: offers.favoritesTemplate.filter(
          (offer) => offer.id !== id
        ),
        favoritesOffer: offers.favoritesOffer,
      }

      await mutate([GET_COLLECTIVE_FAVORITES], newFavoriteOffers, {
        revalidate: false,
      })
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
      <h1 className={styles['title']}>Mes Favoris</h1>
      {offers.favoritesTemplate.length === 0 ? (
        <OffersFavoritesNoResult />
      ) : (
        <ul className={styles['favorite-list']}>
          {offers.favoritesTemplate.map((offer) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                {
                  <AdageOfferListCard
                    offer={offer}
                    afterFavoriteChange={(isFavorite) =>
                      favoriteChangeHandler(isFavorite, offer.id)
                    }
                  />
                }
              </li>
            )
          })}
        </ul>
      )}
    </>
  )
}
