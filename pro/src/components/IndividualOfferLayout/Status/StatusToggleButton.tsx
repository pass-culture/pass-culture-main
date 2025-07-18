import { useRef, useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { formatDateTimeParts, isDateValid } from 'commons/utils/date'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface StatusToggleButtonProps {
  offer: GetIndividualOfferResponseModel
}

export const StatusToggleButton = ({ offer }: StatusToggleButtonProps) => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()

  const toggleButtonRef = useRef<HTMLButtonElement>(null)

  const isPublicationDateInFuture =
    isDateValid(offer.publicationDate) &&
    new Date(offer.publicationDate) > new Date()
  const [
    isPublicationConfirmationModalOpen,
    setIsPublicationConfirmationModalOpen,
  ] = useState(false)

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
      notification.success(
        `L’offre a bien été ${offer.isActive ? 'mise en pause' : 'publiée'}.`
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
        refToFocusOnClose={toggleButtonRef}
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
        ref={toggleButtonRef}
      >
        {offer.status === OfferStatus.INACTIVE ? 'Publier' : 'Mettre en pause'}
      </Button>
    </>
  )
}
