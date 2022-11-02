import React, { useCallback } from 'react'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface IStatusToggleButton {
  offerId: string
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
  const toggleOfferActiveStatus = useCallback(() => {
    api
      // FIX ME: we could send nonHumanizedId and remove dehumanization in api
      // but this involves to modify EAC too
      // @ts-expect-error: type string is not assignable to type number
      .patchOffersActiveStatus({ ids: [offerId], isActive: !isActive })
      .then(() => {
        reloadOffer()
        notification.success(
          `L’offre a bien été ${isActive ? 'désactivée' : 'publiée'}.`
        )
      })
      .catch(() => {
        notification.error(
          'Une erreur est survenue, veuillez réessayer ultérieurement.'
        )
      })
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
