import React from 'react'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import useNotification from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface StatusToggleButtonProps {
  offerId: number
  isActive: boolean
  status: OfferStatus
}

const StatusToggleButton = ({
  offerId,
  isActive,
  status,
}: StatusToggleButtonProps) => {
  const notification = useNotification()
  const { reloadOffer } = useIndividualOfferContext()

  const toggleOfferActiveStatus = async () => {
    try {
      await api.patchOffersActiveStatus({ ids: [offerId], isActive: !isActive })
      await reloadOffer()
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

export default StatusToggleButton
