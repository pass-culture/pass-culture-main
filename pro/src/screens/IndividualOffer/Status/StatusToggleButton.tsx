import React from 'react'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface StatusToggleButtonProps {
  offerId: number
  isActive: boolean
  status: OfferStatus
  setOffer: ((offer: IndividualOffer | null) => void) | null
}

const StatusToggleButton = ({
  offerId,
  isActive,
  status,
  setOffer,
}: StatusToggleButtonProps) => {
  const notification = useNotification()

  const reloadOffer = async () => {
    const response = await getIndividualOfferAdapter(offerId)
    if (response.isOk) {
      setOffer && setOffer(response.payload)
    } else {
      notification.error(response.message)
    }
  }

  const toggleOfferActiveStatus = async () => {
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
