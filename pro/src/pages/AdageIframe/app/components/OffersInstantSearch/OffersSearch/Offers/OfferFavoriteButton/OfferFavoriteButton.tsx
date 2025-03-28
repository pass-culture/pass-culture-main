import { MouseEvent, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useNotification } from 'commons/hooks/useNotification'
import fullStarIcon from 'icons/full-star.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types'
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
  playlistId?: number
}

export const OfferFavoriteButton = ({
  offer,
  queryId,
  afterFavoriteChange,
  isInSuggestions,
  className,
  viewType,
  playlistId,
}: OfferFavoriteButtonProps): JSX.Element => {
  const [isFavorite, setIsFavorite] = useState(
    isCollectiveOfferTemplate(offer) ? offer.isFavorite : false
  )
  const [isLoading, setIsLoading] = useState(false)
  const { setFavoriteCount } = useAdageUser()

  const notify = useNotification()

  const removeFromFavorites = async () => {
    setIsFavorite(false)
    try {
      await apiAdage.deleteFavoriteForCollectiveOfferTemplate(offer.id)
      //  Decrease adage user favorite count for header
      setFavoriteCount?.((count) => count - 1)

      notify.success('Supprimé de vos favoris')

      apiAdage.logFavOfferButtonClick({
        offerId: offer.id,
        queryId,
        iframeFrom: location.pathname,
        isFavorite: false,
        isFromNoResult: isInSuggestions,
        vueType: viewType,
        playlistId,
      })

      afterFavoriteChange?.(false)
    } catch {
      setIsFavorite(true)
    }
    setIsLoading(false)
  }

  const addToFavorites = async () => {
    setIsFavorite(true)
    try {
      await apiAdage.postCollectiveTemplateFavorites(offer.id)

      //  Increase adage user favorite count for header
      setFavoriteCount?.((count) => count + 1)

      notify.success('Ajouté à vos favoris')

      apiAdage.logFavOfferButtonClick({
        offerId: offer.id,
        queryId,
        iframeFrom: location.pathname,
        isFavorite: true,
        isFromNoResult: isInSuggestions,
        vueType: viewType,
        playlistId,
      })

      afterFavoriteChange?.(true)
    } catch {
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

  const buttonText = `${isFavorite ? 'Supprimer des ' : 'Mettre en '} favoris`

  return (
    <ListIconButton
      icon={isFavorite ? fullStarIcon : strokeStarIcon}
      className={className}
      dataTestid={`favorite-${isFavorite ? 'active' : 'inactive'}`}
      onClick={handleFavoriteClick}
      variant={ListIconButtonVariant.PRIMARY}
      tooltipContent={<>{buttonText}</>}
    />
  )
}
