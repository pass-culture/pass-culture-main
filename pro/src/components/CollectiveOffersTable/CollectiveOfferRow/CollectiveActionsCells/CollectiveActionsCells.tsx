import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { getErrorCode, isErrorAPIError } from 'apiClient/helpers'
import {
  CollectiveBookingStatus,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  CollectiveBookingsEvents,
  Events,
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
} from 'commons/core/FirebaseEvents/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import { createOfferFromTemplate } from 'commons/core/OfferEducational/utils/createOfferFromTemplate'
import { duplicateBookableOffer } from 'commons/core/OfferEducational/utils/duplicateBookableOffer'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { getCollectiveOffersSwrKeys } from 'commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  isDateValid,
} from 'commons/utils/date'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { canArchiveCollectiveOffer } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import { CancelCollectiveBookingModal } from 'components/CancelCollectiveBookingModal/CancelCollectiveBookingModal'
import fullClearIcon from 'icons/full-clear.svg'
import fullCopyIcon from 'icons/full-duplicate.svg'
import fullPenIcon from 'icons/full-edit.svg'
import fullHideIcon from 'icons/full-hide.svg'
import fullNextIcon from 'icons/full-next.svg'
import fullPlusIcon from 'icons/full-plus.svg'
import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeThingIcon from 'icons/stroke-thing.svg'
import styles from 'styles/components/Cells.module.scss'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import { BookingLinkCell } from './BookingLinkCell'
import { DuplicateOfferDialog } from './DuplicateOfferDialog/DuplicateOfferDialog'

export interface CollectiveActionsCellsProps {
  offer: CollectiveOfferResponseModel
  editionOfferLink: string
  urlSearchFilters: CollectiveSearchFiltersParams
  deselectOffer: (offer: CollectiveOfferResponseModel) => void
  isSelected: boolean
  headers?: string
  className?: string
}

const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

function hasOfferAnyEditionActionAllowed(offer: CollectiveOfferResponseModel) {
  return offer.allowedActions.some((action) =>
    [
      CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
      CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
    ].includes(action)
  )
}

export const CollectiveActionsCells = ({
  offer,
  editionOfferLink,
  urlSearchFilters,
  deselectOffer,
  isSelected,
  headers,
  className,
}: CollectiveActionsCellsProps) => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCancelledBookingModalOpen, setIsCancelledBookingModalOpen] =
    useState(false)
  const [isArchivedModalOpen, setIsArchivedModalOpen] = useState(false)
  const isLocalStorageAvailable = localStorageAvailable()
  const shouldDisplayModal =
    !isLocalStorageAvailable ||
    localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY) !== 'true'

  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isNewOffersAndBookingsActive,
    isInTemplateOffersPage: offer.isShowcase,
    urlSearchFilters,
    selectedOffererId: selectedOffererId?.toString(),
  })

  const { mutate } = useSWRConfig()

  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const eventDateFormated = isDateValid(offer.stocks[0].beginningDatetime)
    ? formatBrowserTimezonedDateAsUTC(
        new Date(offer.stocks[0].beginningDatetime),
        FORMAT_ISO_DATE_ONLY
      )
    : ''
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${offer.booking?.id}`

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
      notify,
      offer.id,
      undefined,
      isMarseilleActive
    )
  }

  const handleCreateOfferClick = async () => {
    if (offer.isShowcase) {
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
          notify,
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
      await duplicateBookableOffer(navigate, notify, offer.id)
    }
  }

  const apiFilters = {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const cancelBooking = async () => {
    if (!offer.id) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.cancelCollectiveOfferBooking(offer.id)
      await mutate(collectiveOffersQueryKeys)
      if (isSelected) {
        deselectOffer(offer)
      }
      setIsCancelledBookingModalOpen(false)

      const cancelSucessNotification = areCollectiveNewStatusesEnabled
        ? 'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
        : 'La réservation sur cette offre a été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'
      notify.success(cancelSucessNotification, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    } catch (error) {
      if (isErrorAPIError(error) && getErrorCode(error) === 'NO_BOOKING') {
        notify.error(
          'Cette offre n’a aucune réservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
        )
        return
      }
      notify.error(
        'Une erreur est survenue lors de l’annulation de la réservation.',
        {
          duration: NOTIFICATION_LONG_SHOW_DURATION,
        }
      )
    }
  }

  const archiveOffer = async () => {
    if (!offer.id) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      if (offer.isShowcase) {
        await api.patchCollectiveOffersTemplateArchive({ ids: [offer.id] })
      } else {
        await api.patchCollectiveOffersArchive({ ids: [offer.id] })
      }
      await mutate(collectiveOffersQueryKeys)
      if (isSelected) {
        deselectOffer(offer)
      }
      setIsArchivedModalOpen(false)
      notify.success('Une offre a bien été archivée', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    } catch {
      notify.error('Une erreur est survenue lors de l’archivage de l’offre', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
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

  const canDuplicateOffer = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferAllowedAction.CAN_DUPLICATE
      )
    : offer.displayedStatus !== CollectiveOfferDisplayedStatus.DRAFT

  const canCreateBookableOffer = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
      )
    : offer.isShowcase &&
      ![
        CollectiveOfferDisplayedStatus.DRAFT,
        CollectiveOfferDisplayedStatus.PENDING,
      ].includes(offer.displayedStatus)

  const canArchiveOffer = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        offer.isShowcase
          ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
          : CollectiveOfferAllowedAction.CAN_ARCHIVE
      )
    : canArchiveCollectiveOffer(offer)

  const canPublishOffer = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
      )
    : false

  const canHideOffer = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferTemplateAllowedAction.CAN_HIDE
      )
    : false

  const noActionsAllowed = areCollectiveNewStatusesEnabled
    ? offer.allowedActions.length === 0
    : offer.isShowcase &&
      [
        CollectiveOfferDisplayedStatus.ARCHIVED,
        CollectiveOfferDisplayedStatus.PENDING,
      ].includes(offer.displayedStatus)

  const canEditOffer = areCollectiveNewStatusesEnabled
    ? hasOfferAnyEditionActionAllowed(offer)
    : offer.isEditable &&
      !offer.isPublicApi &&
      offer.status !== CollectiveOfferStatus.ARCHIVED

  const isBookingCancellable = areCollectiveNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferAllowedAction.CAN_CANCEL
      )
    : offer.status === CollectiveOfferStatus.SOLD_OUT &&
      offer.booking &&
      (offer.booking.booking_status === CollectiveBookingStatus.PENDING ||
        offer.booking.booking_status === CollectiveBookingStatus.CONFIRMED)

  const offerActivationWording =
    'Votre offre est maintenant active et visible dans ADAGE'
  const offerDeactivationWording = `Votre offre est ${areCollectiveNewStatusesEnabled ? 'mise en pause' : 'désactivée'} et n’est plus visible sur ADAGE`

  const activateOffer = async () => {
    const { isActive, id } = offer
    try {
      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: [id],
        isActive: !isActive,
      })

      notify.success(
        !isActive ? offerActivationWording : offerDeactivationWording
      )
    } catch {
      return notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } de votre offre.`
      )
    }

    await mutate(collectiveOffersQueryKeys)
  }

  return (
    <td
      className={cn(styles['offers-table-cell'], styles['actions-column'], className)}
      headers={headers}
    >
      <div className={styles['actions-column-container']}>
        {(offer.status === CollectiveOfferStatus.SOLD_OUT ||
          offer.status === CollectiveOfferStatus.EXPIRED) &&
          offer.booking && (
            <BookingLinkCell
              bookingId={offer.booking.id}
              bookingStatus={offer.booking.booking_status}
              offerEventDate={offer.stocks[0].beginningDatetime}
              offerId={offer.id}
            />
          )}
        <DropdownMenu.Root modal={false}>
          <DropdownMenu.Trigger className={styles['dropdown-button']} asChild>
            <ListIconButton
              icon={fullThreeDotsIcon}
              title="Action"
              className={noActionsAllowed ? styles['dropdown-button-hide'] : ''}
            >
              Voir les actions
            </ListIconButton>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content className={styles['pop-in']} align="start">
              <div className={styles['menu']}>
                {(offer.status === CollectiveOfferStatus.SOLD_OUT ||
                  offer.status === CollectiveOfferStatus.EXPIRED) &&
                  offer.booking && (
                    <>
                      <DropdownMenu.Item
                        className={styles['menu-item']}
                        asChild
                      >
                        <ButtonLink
                          to={bookingLink}
                          icon={fullNextIcon}
                          onClick={() =>
                            logEvent(
                              CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
                              {
                                from: location.pathname,
                                offerId: offer.id,
                                offerType: 'collective',
                                offererId: selectedOffererId?.toString(),
                              }
                            )
                          }
                        >
                          Voir la{' '}
                          {offer.booking.booking_status ===
                          CollectiveBookingStatus.PENDING
                            ? 'préréservation'
                            : 'réservation'}
                        </ButtonLink>
                      </DropdownMenu.Item>
                      <DropdownMenu.Separator
                        className={cn(
                          styles['separator'],
                          styles['tablet-only']
                        )}
                      />
                    </>
                  )}
                {canDuplicateOffer && (
                  <DropdownMenu.Item
                    className={styles['menu-item']}
                    onSelect={handleCreateOfferClick}
                  >
                    <Button icon={fullCopyIcon} variant={ButtonVariant.TERNARY}>
                      Dupliquer
                    </Button>
                  </DropdownMenu.Item>
                )}
                {canCreateBookableOffer && (
                  <DropdownMenu.Item
                    className={styles['menu-item']}
                    onSelect={handleCreateOfferClick}
                  >
                    <Button icon={fullPlusIcon} variant={ButtonVariant.TERNARY}>
                      Créer une offre réservable
                    </Button>
                  </DropdownMenu.Item>
                )}
                {canEditOffer && (
                  <DropdownMenu.Item className={styles['menu-item']} asChild>
                    <ButtonLink
                      to={editionOfferLink}
                      icon={fullPenIcon}
                      className={styles['button']}
                      onClick={handleEditOfferClick}
                    >
                      Modifier
                    </ButtonLink>
                  </DropdownMenu.Item>
                )}
                {canPublishOffer && (
                  <DropdownMenu.Item
                    className={styles['menu-item']}
                    onSelect={activateOffer}
                  >
                    <Button
                      icon={strokeCheckIcon}
                      variant={ButtonVariant.TERNARY}
                    >
                      Publier
                    </Button>
                  </DropdownMenu.Item>
                )}
                {canHideOffer && (
                  <DropdownMenu.Item
                    className={styles['menu-item']}
                    onSelect={activateOffer}
                  >
                    <Button icon={fullHideIcon} variant={ButtonVariant.TERNARY}>
                      {areCollectiveNewStatusesEnabled
                        ? 'Mettre en pause'
                        : 'Masquer la publication'}
                    </Button>
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
                      asChild
                    >
                      <Button
                        icon={fullClearIcon}
                        variant={ButtonVariant.QUATERNARYPINK}
                        className={styles['button-cancel-booking']}
                      >
                        Annuler la réservation
                      </Button>
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
                          variant={ButtonVariant.TERNARY}
                        >
                          Archiver
                        </Button>
                      </div>
                    </DropdownMenu.Item>
                  </>
                )}
              </div>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
        <DuplicateOfferDialog
          onCancel={() => setIsModalOpen(false)}
          onConfirm={onDialogConfirm}
          isDialogOpen={isModalOpen && shouldDisplayModal}
        />
        <CancelCollectiveBookingModal
          onDismiss={() => setIsCancelledBookingModalOpen(false)}
          onValidate={cancelBooking}
          isFromOffer
          isDialogOpen={isCancelledBookingModalOpen}
        />
        <ArchiveConfirmationModal
          onDismiss={() => setIsArchivedModalOpen(false)}
          onValidate={archiveOffer}
          offer={offer}
          isDialogOpen={isArchivedModalOpen}
        />
      </div>
    </td>
  )
}
