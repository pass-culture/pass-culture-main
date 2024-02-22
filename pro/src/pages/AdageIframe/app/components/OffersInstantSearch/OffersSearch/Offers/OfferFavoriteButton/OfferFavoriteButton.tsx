import cn from 'classnames'
import { useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import fullStarIcon from 'icons/full-star.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import ListIconButton from 'ui-kit/ListIconButton'

import styles from './OfferFavoriteButton.module.scss'

export interface OfferFavoriteButtonProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  queryId?: string
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  className?: string
}

const OfferFavoriteButton = ({
  offer,
  queryId,
  afterFavoriteChange,
  isInSuggestions,
  className,
}: OfferFavoriteButtonProps): JSX.Element => {
  const [isFavorite, setIsFavorite] = useState(offer.isFavorite)
  const [isLoading, setIsLoading] = useState(false)
  const { setFavoriteCount } = useAdageUser()

  const notify = useNotification()

  const removeFromFavorites = async () => {
    setIsFavorite(false)
    try {
      await (offer.isTemplate
        ? apiAdage.deleteFavoriteForCollectiveOfferTemplate(offer.id)
        : apiAdage.deleteFavoriteForCollectiveOffer(offer.id))
      //  Decrease adage user favorite count for header
      setFavoriteCount?.((count) => count - 1)

      notify.success('Supprimé de vos favoris')

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logFavOfferButtonClick({
        offerId: offer.id,
        queryId: queryId,
        iframeFrom: location.pathname,
        isFavorite: false,
        isFromNoResult: isInSuggestions,
      })

      afterFavoriteChange?.(false)
    } catch (error) {
      setIsFavorite(true)
    }
    setIsLoading(false)
  }

  const addToFavorites = async () => {
    setIsFavorite(true)
    try {
      await (offer.isTemplate
        ? apiAdage.postCollectiveTemplateFavorites(offer.id)
        : apiAdage.postCollectiveOfferFavorites(offer.id))

      //  Increase adage user favorite count for header
      setFavoriteCount?.((count) => count + 1)

      notify.success('Ajouté à vos favoris')

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logFavOfferButtonClick({
        offerId: offer.id,
        queryId: queryId,
        iframeFrom: location.pathname,
        isFavorite: true,
        isFromNoResult: isInSuggestions,
      })

      afterFavoriteChange?.(true)
    } catch (error) {
      setIsFavorite(false)
    }
    setIsLoading(false)
  }

  const handleFavoriteClick = function () {
    if (isLoading) {
      return
    }

    setIsLoading(true)

    if (isFavorite) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      removeFromFavorites()
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      addToFavorites()
    }
  }

  const buttonText = `${
    isFavorite ? 'Supprimer des ' : 'Enregistrer en '
  } favoris`

  return (
    <ListIconButton
      icon={isFavorite ? fullStarIcon : strokeStarIcon}
      className={cn(styles['favorite-button'], className, {
        [styles['favorite-button-loading']]: isLoading,
        [styles['favorite-button-active']]: isFavorite,
      })}
      onClick={handleFavoriteClick}
    >
      {buttonText}
    </ListIconButton>
  )
}

export default OfferFavoriteButton
