import { MouseEvent, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useNotification } from 'hooks/useNotification'
import fullStarIcon from 'icons/full-star.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  ListIconButton,
  ListIconButtonVariant,
} from 'ui-kit/ListIconButton/ListIconButton'

export interface OfferFavoriteButtonProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  queryId?: string
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  className?: string
  viewType?: 'grid' | 'list'
}

export const OfferFavoriteButton = ({
  offer,
  queryId,
  afterFavoriteChange,
  isInSuggestions,
  className,
  viewType,
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
        vueType: viewType,
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
        vueType: viewType,
      })

      afterFavoriteChange?.(true)
    } catch (error) {
      setIsFavorite(false)
    }
    setIsLoading(false)
  }

  const handleFavoriteClick = function (event: MouseEvent) {
    event.stopPropagation()
    event.preventDefault()
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
      className={className}
      dataTestid={`favorite-${isFavorite ? 'active' : 'inactive'}`}
      onClick={handleFavoriteClick}
      variant={ListIconButtonVariant.PRIMARY}
    >
      {buttonText}
    </ListIconButton>
  )
}
