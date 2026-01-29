import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { getErrorCode, isErrorAPIError } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  type CollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import {
  type CollectiveOffer,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { getCollectiveOffersSwrKeys } from '@/commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import {
  isActionAllowedOnCollectiveOffer,
  isCollectiveOfferEditable,
} from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { storageAvailable } from '@/commons/utils/storageAvailable'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { CancelCollectiveBookingModal } from '@/components/CancelCollectiveBookingModal/CancelCollectiveBookingModal'
import { ShareLinkDrawer } from '@/components/CollectiveOffer/ShareLinkDrawer/ShareLinkDrawer'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullClearIcon from '@/icons/full-clear.svg'
import fullCopyIcon from '@/icons/full-duplicate.svg'
import fullPenIcon from '@/icons/full-edit.svg'
import fullHideIcon from '@/icons/full-hide.svg'
import fullPlusIcon from '@/icons/full-plus.svg'
import fullThreeDotsIcon from '@/icons/full-three-dots.svg'
import strokeCheckIcon from '@/icons/stroke-check.svg'
import strokeThingIcon from '@/icons/stroke-thing.svg'
import { DropdownMenuWrapper } from '@/ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'

import { DuplicateOfferDialog } from './DuplicateOfferDialog/DuplicateOfferDialog'
import styles from './OfferActionsCell.module.scss'

export interface OfferActionsCellProps {
  offer: CollectiveOffer
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
}

const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

export const OfferActionsCell = ({
  offer,
  urlSearchFilters,
}: OfferActionsCellProps) => {
  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCancelledBookingModalOpen, setIsCancelledBookingModalOpen] =
    useState(false)
  const [isArchivedModalOpen, setIsArchivedModalOpen] = useState(false)
  const isLocalStorageAvailable = storageAvailable('localStorage')
  const shouldDisplayModal =
    !isLocalStorageAvailable ||
    localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY) !== 'true'

  const dropdownTriggerRef = useRef<HTMLButtonElement>(null)
  const isTemplateTable = !isCollectiveOfferBookable(offer)

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isInTemplateOffersPage: isTemplateTable,
    urlSearchFilters,
    selectedOffererId,
  })

  const { mutate } = useSWRConfig()

  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')

  const offerId = computeURLCollectiveOfferId(offer.id, isTemplateTable)
  const draftOfferLink =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${offerId}/creation`

  const editionOfferLink =
    draftOfferLink || `/offre/${offerId}/collectif/edition`

  const onDialogConfirm = async (shouldNotDisplayModalAgain: boolean) => {
    logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFERS_MODAL,
      offererId: selectedOffererId?.toString(),
      offerId: offer.id,
      offerType: 'collective',
      offerStatus: offer.displayedStatus,
    })
    if (shouldNotDisplayModalAgain && isLocalStorageAvailable) {
      localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')
    }
    await createOfferFromTemplate(
      navigate,
      snackBar,
      offer.id,
      undefined,
      isMarseilleActive
    )
  }

  const handleCreateOfferClick = async () => {
    if (isTemplateTable) {
      if (!shouldDisplayModal) {
        logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
          from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFERS,
          offererId: selectedOffererId?.toString(),
          offerId: offer.id,
          offerType: 'collective',
          offerStatus: offer.displayedStatus,
        })
        await createOfferFromTemplate(
          navigate,
          snackBar,
          offer.id,
          undefined,
          isMarseilleActive
        )
      }
      setIsModalOpen(true)
    } else {
      logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFERS,
        offererId: selectedOffererId?.toString(),
        offerId: offer.id,
        offerStatus: offer.displayedStatus,
        offerType: 'collective',
      })
      await duplicateBookableOffer(navigate, snackBar, offer.id)
    }
  }

  const apiFilters = {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const cancelBooking = async () => {
    if (!offer.id) {
      snackBar.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.cancelCollectiveOfferBooking(offer.id)
      await mutate(collectiveOffersQueryKeys)
      setIsCancelledBookingModalOpen(false)

      snackBar.success(
        'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
      )
    } catch (error) {
      if (isErrorAPIError(error) && getErrorCode(error) === 'NO_BOOKING') {
        snackBar.error(
          'Cette offre n’a aucune réservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
        )
        return
      }
      snackBar.error(
        'Une erreur est survenue lors de l’annulation de la réservation.'
      )
    }
  }

  const archiveOffer = async () => {
    if (!offer.id) {
      snackBar.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      if (isTemplateTable) {
        await api.patchCollectiveOffersTemplateArchive({ ids: [offer.id] })
      } else {
        await api.patchCollectiveOffersArchive({ ids: [offer.id] })
      }
      await mutate(collectiveOffersQueryKeys)

      setIsArchivedModalOpen(false)
      snackBar.success('Une offre a bien été archivée')
    } catch {
      snackBar.error('Une erreur est survenue lors de l’archivage de l’offre')
    }
  }

  const handleEditOfferClick = () => {
    logEvent(Events.CLICKED_EDIT_COLLECTIVE_OFFER, {
      from: location.pathname,
      offerId: offer.id,
      offerType: 'collective',
      status: offer.displayedStatus,
    })
  }

  const canDuplicateOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_DUPLICATE
  )

  const canCreateBookableOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
  )

  const canArchiveOffer = isActionAllowedOnCollectiveOffer(
    offer,
    isTemplateTable
      ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
      : CollectiveOfferAllowedAction.CAN_ARCHIVE
  )

  const canPublishOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
  )

  const canHideOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_HIDE
  )

  const canShareOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_SHARE
  )

  const noActionsAllowed = offer.allowedActions.length === 0

  const canEditOffer = isCollectiveOfferEditable(offer)

  const isBookingCancellable = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_CANCEL
  )

  const hideOrPublishOffer = async () => {
    const { id } = offer as CollectiveOfferTemplateResponseModel

    const isActive = isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
    )

    try {
      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: [id],
        isActive,
      })

      snackBar.success(
        isActive
          ? 'Votre offre est maintenant active et visible dans ADAGE'
          : 'Votre offre est mise en pause et n’est plus visible sur ADAGE'
      )
    } catch {
      return snackBar.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } de votre offre.`
      )
    }

    await mutate(collectiveOffersQueryKeys)
  }

  return (
    <div className={styles['actions-column']}>
      {!noActionsAllowed && (
        <DropdownMenuWrapper
          title="Voir les actions"
          triggerIcon={fullThreeDotsIcon}
          triggerTooltip
          dropdownTriggerRef={dropdownTriggerRef}
        >
          {canDuplicateOffer && (
            <DropdownMenu.Item
              className={styles['menu-item']}
              onSelect={handleCreateOfferClick}
            >
              <Button
                icon={fullCopyIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                label="Dupliquer"
              />
            </DropdownMenu.Item>
          )}
          {canCreateBookableOffer && (
            <DropdownMenu.Item
              className={styles['menu-item']}
              onSelect={handleCreateOfferClick}
            >
              <Button
                icon={fullPlusIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                label="Créer une offre réservable"
              />
            </DropdownMenu.Item>
          )}
          {canEditOffer && (
            <DropdownMenu.Item className={styles['menu-item']}>
              <Button
                as="a"
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                to={editionOfferLink}
                icon={fullPenIcon}
                onClick={handleEditOfferClick}
                label="Modifier"
              />
            </DropdownMenu.Item>
          )}
          {canPublishOffer && (
            <DropdownMenu.Item
              className={styles['menu-item']}
              onSelect={hideOrPublishOffer}
            >
              <Button
                icon={strokeCheckIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                label="Publier"
              />
            </DropdownMenu.Item>
          )}
          {!isCollectiveOfferBookable(offer) && canShareOffer && (
            <DropdownMenu.Item
              className={styles['menu-item']}
              onSelect={(e) => e.preventDefault()}
            >
              <ShareLinkDrawer offerId={offer.id} />
            </DropdownMenu.Item>
          )}
          {canHideOffer && (
            <DropdownMenu.Item
              className={styles['menu-item']}
              onSelect={hideOrPublishOffer}
            >
              <Button
                icon={fullHideIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                label="Mettre en pause"
              />
            </DropdownMenu.Item>
          )}
          {isBookingCancellable && (
            <>
              <DropdownMenu.Separator
                className={cn(styles['separator'], styles['tablet-only'])}
              />
              <DropdownMenu.Item
                className={cn(styles['menu-item'])}
                onSelect={() => setIsCancelledBookingModalOpen(true)}
              >
                <Button
                  icon={fullClearIcon}
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.BRAND}
                  label="Annuler la réservation"
                />
              </DropdownMenu.Item>
            </>
          )}
          {canArchiveOffer && (
            <>
              <DropdownMenu.Separator
                className={cn(styles['separator'], styles['tablet-only'])}
              />
              <DropdownMenu.Item
                className={cn(styles['menu-item'])}
                onSelect={() => setIsArchivedModalOpen(true)}
                asChild
              >
                <div className={styles['status-filter-label']}>
                  <Button
                    icon={strokeThingIcon}
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    label="Archiver"
                  />
                </div>
              </DropdownMenu.Item>
            </>
          )}
        </DropdownMenuWrapper>
      )}
      <DuplicateOfferDialog
        onCancel={() => setIsModalOpen(false)}
        onConfirm={onDialogConfirm}
        isDialogOpen={isModalOpen && shouldDisplayModal}
        refToFocusOnClose={dropdownTriggerRef}
      />
      <CancelCollectiveBookingModal
        onDismiss={() => setIsCancelledBookingModalOpen(false)}
        onValidate={cancelBooking}
        isFromOffer
        isDialogOpen={isCancelledBookingModalOpen}
        refToFocusOnClose={dropdownTriggerRef}
      />
      <ArchiveConfirmationModal
        onDismiss={() => setIsArchivedModalOpen(false)}
        onValidate={archiveOffer}
        offer={offer}
        isDialogOpen={isArchivedModalOpen}
        refToFocusOnClose={dropdownTriggerRef}
      />
    </div>
  )
}
