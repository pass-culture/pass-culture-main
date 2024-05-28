import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import useNotification from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface StatusToggleButtonProps {
  offerId: number
  isActive: boolean
  status: OfferStatus
}

export const StatusToggleButton = ({
  offerId,
  isActive,
  status,
}: StatusToggleButtonProps) => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()

  const toggleOfferActiveStatus = async () => {
    try {
      await api.patchOffersActiveStatus({ ids: [offerId], isActive: !isActive })
      await mutate([GET_OFFER_QUERY_KEY, offerId])
      notification.success(
        `L’offre a bien été ${isActive ? 'désactivée' : 'publiée'}.`
      )
    } catch (error) {
      notification.error(
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      )
    }
  }

  return (
    <Button
      variant={ButtonVariant.TERNARY}
      disabled={[OfferStatus.PENDING, OfferStatus.REJECTED].includes(status)}
      onClick={toggleOfferActiveStatus}
      icon={status !== OfferStatus.INACTIVE ? fullHideIcon : strokeCheckIcon}
    >
      {status !== OfferStatus.INACTIVE ? 'Désactiver' : 'Publier'}
    </Button>
  )
}
