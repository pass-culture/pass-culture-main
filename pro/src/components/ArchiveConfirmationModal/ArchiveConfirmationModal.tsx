import { useLocation } from 'react-router'

import type {
  CollectiveOfferBookableResponseModel,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import strokeThingIcon from '@/icons/stroke-thing.svg'

interface Offer {
  id: string | number
  displayedStatus: CollectiveOfferDisplayedStatus
}
interface OfferEducationalModalProps<T extends Offer> {
  onDismiss(): void
  onValidate(): void
  offer?:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
    | CollectiveOfferBookableResponseModel
    | CollectiveOfferTemplateResponseModel
  hasMultipleOffers?: boolean
  selectedOffers?: T[]
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement | HTMLAnchorElement>
}

export const ArchiveConfirmationModal = <T extends Offer>({
  onDismiss,
  onValidate,
  hasMultipleOffers = false,
  selectedOffers = [],
  offer,
  isDialogOpen,
  refToFocusOnClose,
}: OfferEducationalModalProps<T>): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  function onConfirmArchive() {
    logEvent(Events.CLICKED_ARCHIVE_COLLECTIVE_OFFER, {
      from: location.pathname,
      offerType: 'collective',
      selected_offers: JSON.stringify(
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
            ]
      ),
    })
    onValidate()
  }

  return (
    <ConfirmDialog
      onCancel={onDismiss}
      onConfirm={onConfirmArchive}
      cancelText="Annuler"
      confirmText={
        hasMultipleOffers ? 'Archiver les offres' : 'Archiver l’offre'
      }
      icon={strokeThingIcon}
      title={
        hasMultipleOffers
          ? 'Êtes-vous sûr de vouloir archiver ces offres ?'
          : 'Êtes-vous sûr de vouloir archiver cette offre ?'
      }
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
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
