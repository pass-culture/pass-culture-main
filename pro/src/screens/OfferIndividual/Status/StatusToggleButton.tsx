import React, { useCallback } from 'react'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface IStatusToggleButton {
  offerId: number
  isActive: boolean
  status: OfferStatus
  reloadOffer: () => void
}

const StatusToggleButton = ({
  offerId,
  isActive,
  status,
  reloadOffer,
}: IStatusToggleButton) => {
  const notification = useNotification()

  const toggleOfferActiveStatus = useCallback(async () => {
    try {
      await api.patchOffersActiveStatus({ ids: [offerId], isActive: !isActive })
      reloadOffer()
      notification.success(
        `L’offre a bien été ${isActive ? 'désactivée' : 'publiée'}.`
      )
    } catch (error) {
      notification.error(
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      )
    }
  }, [offerId, isActive, reloadOffer])

  return (
    <Button
      variant={ButtonVariant.TERNARY}
      disabled={[OfferStatus.PENDING, OfferStatus.REJECTED].includes(status)}
      onClick={toggleOfferActiveStatus}
      Icon={
        status !== OfferStatus.INACTIVE
          ? StatusInactiveIcon
          : StatusValidatedIcon
      }
    >
      {status !== OfferStatus.INACTIVE ? 'Désactiver' : 'Publier'}
    </Button>
  )
}

export default StatusToggleButton
