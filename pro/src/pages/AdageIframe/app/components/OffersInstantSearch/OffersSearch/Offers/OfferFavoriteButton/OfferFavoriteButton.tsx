import cn from 'classnames'
import { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import fullBookmarkIcon from 'icons/full-bookmark.svg'
import strokeBookmarkIcon from 'icons/stroke-bookmark.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './OfferFavoriteButton.module.scss'

const OfferFavoriteButton = ({
  offer,
  afterFavoriteChange,
}: {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  afterFavoriteChange?: (isFavorite: boolean) => void
}): JSX.Element => {
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
      setFavoriteCount?.(count => count - 1)

      notify.success('Supprimé de vos favoris')

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
      setFavoriteCount?.(count => count + 1)

      notify.success('Ajouté à vos favoris')

      afterFavoriteChange?.(true)
    } catch (error) {
      setIsFavorite(false)
    }
    setIsLoading(false)
  }

  const handleFavoriteClick = function () {
    setIsLoading(true)

    if (isFavorite) {
      removeFromFavorites()
    } else {
      addToFavorites()
    }
  }

  const buttonText = `${
    isFavorite ? 'Supprimer des ' : 'Enregistrer en '
  } favoris`

  return (
    <Button
      icon={isFavorite ? fullBookmarkIcon : strokeBookmarkIcon}
      className={cn(styles['favorite-button'], {
        [styles['favorite-button-active']]: isFavorite,
      })}
      variant={ButtonVariant.TERNARY}
      onClick={handleFavoriteClick}
      hasTooltip
      disabled={isLoading}
    >
      {buttonText}
    </Button>
  )
}

export default OfferFavoriteButton
