import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  CollectiveBookingsEvents,
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import { createOfferFromBookableOffer } from 'core/OfferEducational/utils/createOfferFromBookableOffer'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import copyIcon from 'icons/full-duplicate.svg'
import penIcon from 'icons/full-edit.svg'
import nextIcon from 'icons/full-next.svg'
import fullPlusIcon from 'icons/full-plus.svg'
import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  isDateValid,
} from 'utils/date'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import styles from '../OfferItem.module.scss'

import { BookingLinkCell } from './BookingLinkCell'
import { DuplicateOfferDialog } from './DuplicateOfferCell/DuplicateOfferDialog/DuplicateOfferDialog'

interface CollectiveActionsCellsProps {
  offer: CollectiveOfferResponseModel
  editionOfferLink: string
}

const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

export const CollectiveActionsCells = ({
  offer,
  editionOfferLink,
}: CollectiveActionsCellsProps) => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const isLocalStorageAvailable = localStorageAvailable()
  const shouldDisplayModal =
    !isLocalStorageAvailable ||
    localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY) !== 'true'

  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  if (!isDateValid(offer.stocks[0].beginningDatetime)) {
    return null
  }

  const eventDateFormated = formatBrowserTimezonedDateAsUTC(
    new Date(offer.stocks[0].beginningDatetime),
    FORMAT_ISO_DATE_ONLY
  )
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${offer.booking?.id}`

  const onDialogConfirm = async (shouldNotDisplayModalAgain: boolean) => {
    logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS_MODAL,
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
          from: OFFER_FROM_TEMPLATE_ENTRIES.OFFERS,
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
      await createOfferFromBookableOffer(navigate, notify, offer.id)
    }
  }

  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-container']}>
        {(offer.status === OfferStatus.SOLD_OUT ||
          offer.status === OfferStatus.EXPIRED) &&
          offer.booking && (
            <BookingLinkCell
              bookingId={offer.booking.id}
              bookingStatus={offer.booking.booking_status}
              offerEventDate={offer.stocks[0].beginningDatetime}
            />
          )}
        <DropdownMenu.Root modal={false}>
          <DropdownMenu.Trigger className={styles['dropdown-button']} asChild>
            <ListIconButton icon={fullThreeDotsIcon} title="Action">
              Voir les actions
            </ListIconButton>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content className={styles['pop-in']} align="start">
              <div className={styles['menu']}>
                {(offer.status === OfferStatus.SOLD_OUT ||
                  offer.status === OfferStatus.EXPIRED) &&
                  offer.booking && (
                    <>
                      <DropdownMenu.Item
                        className={styles['menu-item']}
                        asChild
                      >
                        <ButtonLink
                          link={{ to: bookingLink, isExternal: false }}
                          icon={nextIcon}
                          onClick={() =>
                            logEvent(
                              CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
                              {
                                from: location.pathname,
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
                <DropdownMenu.Item
                  className={styles['menu-item']}
                  onSelect={handleCreateOfferClick}
                >
                  <Button
                    icon={offer.isShowcase ? fullPlusIcon : copyIcon}
                    variant={ButtonVariant.TERNARY}
                  >
                    {offer.isShowcase
                      ? 'Créer une offre réservable'
                      : 'Dupliquer'}
                  </Button>
                </DropdownMenu.Item>
                {offer.isEditable && !offer.isPublicApi && (
                  <DropdownMenu.Item className={styles['menu-item']} asChild>
                    <ButtonLink
                      link={{ to: editionOfferLink, isExternal: false }}
                      icon={penIcon}
                      className={styles['button']}
                    >
                      Modifier
                    </ButtonLink>
                  </DropdownMenu.Item>
                )}
              </div>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
        {isModalOpen && shouldDisplayModal && (
          <DuplicateOfferDialog
            onCancel={() => setIsModalOpen(false)}
            onConfirm={onDialogConfirm}
          />
        )}
      </div>
    </td>
  )
}
