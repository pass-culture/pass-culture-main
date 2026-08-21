import type {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokeArchiveIcon from '@/icons/stroke-archive.svg'

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
    | CollectiveOfferResponseModel
    | CollectiveOfferTemplateResponseModel
  hasMultipleOffers?: boolean
  selectedOffers?: T[]
  isDialogOpen: boolean
}

export const ArchiveConfirmationModal = <T extends Offer>({
  onDismiss,
  onValidate,
  hasMultipleOffers = false,
  selectedOffers = [],
  offer,
  isDialogOpen,
}: OfferEducationalModalProps<T>): JSX.Element => {
  const { logEvent } = useAnalytics()

  function onConfirmArchive() {
    logEvent(Events.CLICKED_ARCHIVE_COLLECTIVE_OFFER, {
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
    <SimpleModal
      iconPath={strokeArchiveIcon}
      title={
        hasMultipleOffers
          ? 'Êtes-vous sûr de vouloir archiver ces offres ?'
          : 'Êtes-vous sûr de vouloir archiver cette offre ?'
      }
      isOpen={isDialogOpen}
      onClose={onDismiss}
      actionButtons={[
        <Button
          key="cancel"
          onClick={onDismiss}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler"
        />,
        <Button
          key="confirm"
          onClick={onConfirmArchive}
          color={ButtonColor.DANGER}
          label={hasMultipleOffers ? 'Archiver les offres' : 'Archiver l’offre'}
        />,
      ]}
    >
      <p>Une offre archivée ne peut pas être désarchivée.</p>
      <strong>Cette action est irréversible.</strong>
      <p>
        Vous pourrez la retrouver facilement en filtrant sur le statut
        “archivée”.
      </p>
    </SimpleModal>
  )
}
