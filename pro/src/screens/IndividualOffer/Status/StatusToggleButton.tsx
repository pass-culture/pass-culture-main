import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { formatDateTimeParts, isDateValid } from 'utils/date'

export interface StatusToggleButtonProps {
  offer: GetIndividualOfferResponseModel
}

export const StatusToggleButton = ({ offer }: StatusToggleButtonProps) => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()
  const isPublicationDateInFuture =
    isDateValid(offer.publicationDate) &&
    new Date(offer.publicationDate) > new Date()
  const [
    isPublicationConfirmationModalOpen,
    setIsPublicationConfirmationModalOpen,
  ] = useState(false)
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const { date: publicationDate, time: publicationTime } = formatDateTimeParts(
    offer.publicationDate
  )

  const toggleOfferActiveStatus = async () => {
    if (
      isPublicationDateInFuture &&
      !offer.isActive &&
      !isPublicationConfirmationModalOpen
    ) {
      setIsPublicationConfirmationModalOpen(true)
      return
    }

    try {
      await api.patchOffersActiveStatus({
        ids: [offer.id],
        isActive: !offer.isActive,
      })
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
      const deactivationWording = areCollectiveNewStatusesEnabled
        ? 'mise en pause'
        : 'désactivée'
      notification.success(
        `L’offre a bien été ${offer.isActive ? deactivationWording : 'publiée'}.`
      )
      if (isPublicationConfirmationModalOpen) {
        logEvent(Events.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER, {
          offerId: offer.id,
          offerType: 'individual',
        })
      }
    } catch {
      notification.error(
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      )
    } finally {
      setIsPublicationConfirmationModalOpen(false)
    }
  }

  const deactivateWording = areCollectiveNewStatusesEnabled
    ? 'Mettre en pause'
    : 'Désactiver'

  return (
    <>
      <ConfirmDialog
        title={`Attention, vous allez publier une offre programmée pour le ${publicationDate} à ${publicationTime}.`}
        secondTitle="Êtes-vous sûr de vouloir continuer ?"
        cancelText="Annuler"
        confirmText="Confirmer la publication"
        onCancel={() => setIsPublicationConfirmationModalOpen(false)}
        onConfirm={toggleOfferActiveStatus}
        open={isPublicationConfirmationModalOpen}
      />

      <Button
        variant={ButtonVariant.TERNARY}
        disabled={[OfferStatus.PENDING, OfferStatus.REJECTED].includes(
          offer.status
        )}
        onClick={toggleOfferActiveStatus}
        icon={
          offer.status === OfferStatus.INACTIVE ? strokeCheckIcon : fullHideIcon
        }
      >
        {offer.status === OfferStatus.INACTIVE ? 'Publier' : deactivateWording}
      </Button>
    </>
  )
}
