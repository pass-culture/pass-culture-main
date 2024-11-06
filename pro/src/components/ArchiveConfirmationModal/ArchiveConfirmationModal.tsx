import { useLocation } from 'react-router-dom'

import {
  CollectiveOfferResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeThingIcon from 'icons/stroke-thing.svg'

interface OfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
  hasMultipleOffers?: boolean
  selectedOffers?: CollectiveOfferResponseModel[]
  isDialogOpen: boolean
}

export const ArchiveConfirmationModal = ({
  onDismiss,
  onValidate,
  hasMultipleOffers = false,
  selectedOffers = [],
  offer,
  isDialogOpen,
}: OfferEducationalModalProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  function onConfirmArchive() {
    logEvent(Events.CLICKED_ARCHIVE_COLLECTIVE_OFFER, {
      from: location.pathname,
      selected_offers:
        selectedOffers.length > 0
          ? selectedOffers.map((offer) => ({
              offerId: offer.id.toString(),
              offerStatus: offer.displayedStatus,
            }))
          : [
              {
                offerId: offer?.id.toString(),
                offerStatus: offer?.displayedStatus,
              },
            ],
    })
    onValidate()
  }

  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onConfirmArchive}
      cancelText="Annuler"
      confirmText={
        hasMultipleOffers ? 'Archiver les offres ' : 'Archiver l’offre'
      }
      icon={strokeThingIcon}
      title={
        hasMultipleOffers
          ? 'Êtes-vous sûr de vouloir archiver ces offres ?'
          : 'Êtes-vous sûr de vouloir archiver cette offre ?'
      }
      open={isDialogOpen}
    >
      <p>
        Une offre archivée ne peut pas être désarchivée, cette action est
        irréversible
      </p>
      <p>
        Vous pourrez la retrouver facilement en filtrant sur le statut
        “archivée”.
      </p>
    </ConfirmDialog>
  )
}
