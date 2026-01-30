import { type MouseEvent, useState } from 'react'

import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullStarIcon from '@/icons/full-star.svg'
import strokeStarIcon from '@/icons/stroke-star.svg'
import { useAdageUser } from '@/pages/AdageIframe/app/hooks/useAdageUser'
import { isCollectiveOfferTemplate } from '@/pages/AdageIframe/app/types'

export interface OfferFavoriteButtonProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  queryId?: string
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  viewType?: 'grid' | 'list'
  playlistId?: number
}

export const OfferFavoriteButton = ({
  offer,
  queryId,
  afterFavoriteChange,
  isInSuggestions,
  viewType,
  playlistId,
}: OfferFavoriteButtonProps): JSX.Element => {
  const [isFavorite, setIsFavorite] = useState(
    isCollectiveOfferTemplate(offer) ? offer.isFavorite : false
  )
  const [isLoading, setIsLoading] = useState(false)
  const { setFavoriteCount } = useAdageUser()

  const snackBar = useSnackBar()

  const removeFromFavorites = async () => {
    setIsFavorite(false)
    try {
      await apiAdage.deleteFavoriteForCollectiveOfferTemplate(offer.id)
      //  Decrease adage user favorite count for header
      setFavoriteCount?.((count) => count - 1)

      snackBar.success('Supprimé de vos favoris')

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

      snackBar.success('Ajouté à vos favoris')

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

  const handleFavoriteClick = (event: MouseEvent) => {
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
    <Button
      variant={ButtonVariant.SECONDARY}
      color={ButtonColor.BRAND}
      icon={isFavorite ? fullStarIcon : strokeStarIcon}
      data-testid={`favorite-${isFavorite ? 'active' : 'inactive'}`}
      onClick={handleFavoriteClick}
      tooltip={buttonText}
    />
  )
}
