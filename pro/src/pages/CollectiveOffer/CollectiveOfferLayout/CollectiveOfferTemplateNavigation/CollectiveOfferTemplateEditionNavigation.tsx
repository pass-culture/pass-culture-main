import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { mutate } from 'swr'

import { apiNew } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { ShareLinkDrawer } from '@/components/CollectiveOffer/ShareLinkDrawer/ShareLinkDrawer'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullArchiveIcon from '@/icons/full-archive.svg'
import fullCopyIcon from '@/icons/full-duplicate.svg'
import fullPlusIcon from '@/icons/full-plus.svg'
import fullShowIcon from '@/icons/full-show.svg'

import styles from './CollectiveOfferTemplateNavigation.module.scss'

export interface CollectiveOfferTemplateEditionNavigationProps {
  offer?: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferTemplateEditionNavigation = ({
  offer,
}: CollectiveOfferTemplateEditionNavigationProps): JSX.Element => {
  const offerId = offer?.id ?? 0
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')

  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false)

  const id = computeURLCollectiveOfferId(offerId, true)

  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const adagePreviewButtonRef = useRef<HTMLAnchorElement>(null)
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const archiveOffer = async () => {
    if (!offerId) {
      snackBar.error("L'identifiant de l'offre n'est pas valide.")
      return
    }
    try {
      await apiNew.patchCollectiveOffersTemplateArchive({
        body: { ids: [offerId] },
      })
      await mutate([GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offerId])

      setIsArchiveModalOpen(false)

      snackBar.success("L'offre a bien été archivée")
    } catch {
      snackBar.error("Une erreur est survenue lors de l'archivage de l'offre")
    }
  }

  const onCreateOfferFromTemplate = () => {
    logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      offerId,
      offerType: 'collective',
      offerStatus: offer?.displayedStatus,
    })
    return createOfferFromTemplate(
      navigate,
      snackBar,
      offerId,
      selectedPartnerVenue,
      undefined,
      isMarseilleActive
    )
  }

  const onDuplicateOfferTemplate = () => {
    logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
      offerId,
      offerStatus: offer?.displayedStatus,
      offerType: 'collective',
    })
    return duplicateBookableOffer(
      navigate,
      snackBar,
      offerId,
      selectedPartnerVenue
    )
  }

  const canPreviewOffer =
    offer?.displayedStatus !== CollectiveOfferDisplayedStatus.ARCHIVED

  const canArchiveOffer =
    !!offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
    )

  const canDuplicateOffer =
    !!offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE
    )

  const canCreateBookableOffer =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
    )

  const canShareOffer =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_SHARE
    )

  return (
    <div className={styles['actions-container']}>
      {canPreviewOffer && (
        <Button
          as="a"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          to={`/offre/${id}/collectif/vitrine/apercu`}
          icon={fullShowIcon}
          ref={adagePreviewButtonRef}
          label="Aperçu dans ADAGE"
        />
      )}

      {canArchiveOffer && (
        <Button
          onClick={() => setIsArchiveModalOpen(true)}
          icon={fullArchiveIcon}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.DANGER}
          size={ButtonSize.SMALL}
          ref={archiveButtonRef}
          label="Archiver"
        />
      )}

      {canDuplicateOffer && (
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={fullCopyIcon}
          size={ButtonSize.SMALL}
          onClick={onDuplicateOfferTemplate}
          label="Dupliquer"
        />
      )}

      {canCreateBookableOffer && (
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={fullPlusIcon}
          size={ButtonSize.SMALL}
          onClick={onCreateOfferFromTemplate}
          label="Créer une offre réservable"
        />
      )}
      {canShareOffer && <ShareLinkDrawer offerId={offer.id} />}

      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveModalOpen(false)}
        onValidate={archiveOffer}
        offer={offer}
        isDialogOpen={isArchiveModalOpen}
        refToFocusOnClose={
          archiveButtonRef.current ? archiveButtonRef : adagePreviewButtonRef
        }
      />
    </div>
  )
}
