import cn from 'classnames'
import { useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from '@/commons/core/Notification/constants'
import { isCollectiveOffer } from '@/commons/core/OfferEducational/types'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useNotification } from '@/commons/hooks/useNotification'
import {
  selectCurrentOfferer,
  selectCurrentOffererId,
} from '@/commons/store/offerer/selectors'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import {
  isActionAllowedOnCollectiveOffer,
  isCollectiveOfferEditable,
} from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { pluralizeString } from '@/commons/utils/pluralize'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { CancelCollectiveBookingModal } from '@/components/CancelCollectiveBookingModal/CancelCollectiveBookingModal'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { EducationalInstitutionDetails } from '@/components/EducationalInstitutionDetails/EducationalInstitutionDetails'
import { SynchronizedProviderInformation } from '@/components/SynchronisedProviderInformation/SynchronizedProviderInformation'
import fullArchiveIcon from '@/icons/full-archive.svg'
import fullClearIcon from '@/icons/full-clear.svg'
import fullCopyIcon from '@/icons/full-duplicate.svg'
import fullEditIcon from '@/icons/full-edit.svg'
import fullShowIcon from '@/icons/full-show.svg'
import strokeCalendarIcon from '@/icons/stroke-calendar.svg'
import strokeClockIcon from '@/icons/stroke-clock.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeHomeIcon from '@/icons/stroke-home.svg'
import strokeLocationIcon from '@/icons/stroke-location.svg'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import strokeTeacherIcon from '@/icons/stroke-teacher.svg'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { getLocation } from '@/pages/AdageIframe/app/components/OfferInfos/AdageOffer/AdageOfferDetailsSection/AdageOfferInfoSection'
import { BookableOfferTimeline } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/BookableOfferTimeline/BookableOfferTimeline'
import { DEFAULT_RECAP_VALUE } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/components/constants'
import { formatDateTime } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/components/utils/formatDatetime'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { DetailItem } from '../components/DetailItem/DetailItem'
import styles from './BookableOfferSummary.module.scss'

export type BookableOfferSummaryProps = {
  offer: GetCollectiveOfferResponseModel
}

export const BookableOfferSummary = ({ offer }: BookableOfferSummaryProps) => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offerer = useSelector(selectCurrentOfferer)

  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const duplicateButtonRef = useRef<HTMLButtonElement>(null)
  const adagePreviewButtonRef = useRef<HTMLAnchorElement>(null)
  const cancelBookingButtonRef = useRef<HTMLButtonElement>(null)

  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false)
  const [isCancelBookingModalOpen, setIsCancelBookingModalOpen] =
    useState(false)

  const cancelBooking = async () => {
    if (!offer.id) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.cancelCollectiveOfferBooking(offer.id)
      await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])
      setIsCancelBookingModalOpen(false)
      notify.success(
        'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.',
        {
          duration: NOTIFICATION_LONG_SHOW_DURATION,
        }
      )
    } catch {
      notify.error(
        'Une erreur est survenue lors de l’annulation de la réservation.',
        {
          duration: NOTIFICATION_LONG_SHOW_DURATION,
        }
      )
    }
  }

  const formatDateRangeWithTime = (): string => {
    const { startDatetime, endDatetime } = offer.collectiveStock || {}
    const venueDepartmentCode =
      offer.location?.address?.departmentCode ?? offer.venue.departementCode

    if (!startDatetime || !endDatetime) {
      return DEFAULT_RECAP_VALUE
    }

    const startDate = formatDateTime(
      startDatetime,
      FORMAT_DD_MM_YYYY,
      venueDepartmentCode
    )
    const endDate = formatDateTime(
      endDatetime,
      FORMAT_DD_MM_YYYY,
      venueDepartmentCode
    )
    const startTime = formatDateTime(
      startDatetime,
      "HH'h'mm",
      venueDepartmentCode
    )

    if (startDatetime === endDatetime) {
      return `Le ${startDate} - ${startTime}`
    }

    return `Du ${startDate} au ${endDate} - ${startTime}`
  }

  const archiveOffer = async () => {
    if (!offer.id) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.patchCollectiveOffersArchive({ ids: [offer.id] })
      await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])

      setIsArchiveModalOpen(false)

      notify.success('L’offre a bien été archivée', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    } catch {
      notify.error('Une erreur est survenue lors de l’archivage de l’offre', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }

  const canEditOffer = isCollectiveOfferEditable(offer)

  const canArchiveOffer =
    isCollectiveOffer(offer) &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferAllowedAction.CAN_ARCHIVE
    )

  const canDuplicateOffer =
    isCollectiveOffer(offer) &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferAllowedAction.CAN_DUPLICATE
    )

  const isBookingCancellable = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_CANCEL
  )

  const offerEditLink = `/offre/${offer.id}/collectif/edition`

  const draftOfferLink =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${offer.id}/creation`

  const location = offer.location
    ? getLocation(offer.location, true)
    : 'Localisation à déterminer avec l’enseignant'

  return (
    <BasicLayout mainHeading={offer.name} isStickyActionBarInChild>
      <div className={styles['header-title']}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </div>
      {isCollectiveOffer(offer) && offer.provider?.name && (
        <div className={styles['banner-container']}>
          <SynchronizedProviderInformation providerName={offer.provider.name} />
        </div>
      )}
      <div className={styles['header-description']}>
        <div>
          {offer.imageUrl ? (
            <img
              alt={offer.name}
              src={offer.imageUrl}
              className={styles['image-preview']}
            />
          ) : (
            <div
              className={cn(styles['default-preview'], styles['image-preview'])}
            >
              <SvgIcon alt={offer.name} src={strokeOfferIcon} />
            </div>
          )}
        </div>
        <div className={styles['header-description-info']}>
          <dl className={styles['detail-list']}>
            <DetailItem>n°{offer.id}</DetailItem>
            <DetailItem alt={offer.venue.publicName ?? ''} src={strokeHomeIcon}>
              Proposé par{' '}
              {offer.venue.publicName
                ? offer.venue.publicName
                : offer.venue.name}
            </DetailItem>
            <DetailItem alt={'Date de l’offre'} src={strokeCalendarIcon}>
              {formatDateRangeWithTime()}
            </DetailItem>
            <DetailItem
              alt="Établissement scolaire où se déroule l’offre"
              src={strokeTeacherIcon}
            >
              {offer.institution?.institutionType && offer.institution.name
                ? `${offer.institution.institutionType} ${offer.institution.name} ${offer.institution.postalCode ? `- ${offer.institution.postalCode}` : ''}`
                : DEFAULT_RECAP_VALUE}
            </DetailItem>
            <DetailItem alt="Nombre de participants" src={strokeUserIcon}>
              {offer.collectiveStock?.numberOfTickets
                ? `${offer.collectiveStock.numberOfTickets} ${pluralizeString('participant', offer.collectiveStock.numberOfTickets)}`
                : DEFAULT_RECAP_VALUE}
            </DetailItem>
            <DetailItem alt="Prix de l’offre" src={strokeEuroIcon}>
              {offer.collectiveStock?.price ||
              offer.collectiveStock?.price === 0
                ? `${offer.collectiveStock.price} ${pluralizeString('euro', offer.collectiveStock.price)}`
                : DEFAULT_RECAP_VALUE}
            </DetailItem>
            <DetailItem alt="Adresse de l’offre" src={strokeLocationIcon}>
              {location}
            </DetailItem>
            <DetailItem alt="Date limite de réservation" src={strokeClockIcon}>
              Date limite de réservation :{' '}
              {offer.collectiveStock?.bookingLimitDatetime
                ? formatDateTime(
                    offer.collectiveStock.bookingLimitDatetime,
                    FORMAT_DD_MM_YYYY,
                    offer.venue.departementCode
                  )
                : DEFAULT_RECAP_VALUE}
            </DetailItem>
          </dl>
          <div className={styles['header-actions']}>
            <span className={styles['header-actions-title']}>Actions</span>
            <ul>
              {canEditOffer && (
                <li>
                  <ButtonLink
                    to={draftOfferLink ? draftOfferLink : offerEditLink}
                    aria-label={'Modifier l’offre'}
                    icon={fullEditIcon}
                  >
                    Modifier
                  </ButtonLink>
                </li>
              )}

              {offer.displayedStatus !==
                CollectiveOfferDisplayedStatus.DRAFT && (
                <li>
                  <ButtonLink
                    to={`/offre/${offer.id}/collectif/apercu`}
                    icon={fullShowIcon}
                    ref={adagePreviewButtonRef}
                  >
                    Aperçu
                  </ButtonLink>
                </li>
              )}

              {canDuplicateOffer && (
                <li>
                  <Button
                    variant={ButtonVariant.TERNARY}
                    icon={fullCopyIcon}
                    onClick={async () => {
                      logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
                        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_RECAP,
                        offererId: selectedOffererId?.toString(),
                        offerId: offer.id,
                        offerStatus: offer.displayedStatus,
                        offerType: 'collective',
                      })
                      await duplicateBookableOffer(navigate, notify, offer.id)
                    }}
                    ref={duplicateButtonRef}
                  >
                    Dupliquer
                  </Button>
                </li>
              )}
              {canArchiveOffer && (
                <li>
                  <Button
                    onClick={() => setIsArchiveModalOpen(true)}
                    icon={fullArchiveIcon}
                    variant={ButtonVariant.TERNARY}
                    ref={archiveButtonRef}
                  >
                    Archiver
                  </Button>
                </li>
              )}
              {isBookingCancellable && (
                <li>
                  <Button
                    icon={fullClearIcon}
                    variant={ButtonVariant.TERNARYBRAND}
                    className={styles['button-cancel-booking']}
                    onClick={() => setIsCancelBookingModalOpen(true)}
                    ref={cancelBookingButtonRef}
                  >
                    Annuler la réservation
                  </Button>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>
      <div className={styles['offer-details']}>
        <div
          className={
            offer.institution
              ? styles['timeline-container']
              : styles['partial-timeline-container']
          }
        >
          <BookableOfferTimeline offer={offer} offerer={offerer} />
        </div>
        {offer.institution && (
          <EducationalInstitutionDetails
            educationalInstitution={offer.institution}
            educationalRedactor={offer.booking?.educationalRedactor}
            teacher={offer.teacher}
            newLayout
          />
        )}
      </div>
      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveModalOpen(false)}
        onValidate={archiveOffer}
        offer={offer}
        isDialogOpen={isArchiveModalOpen}
        refToFocusOnClose={
          cancelBookingButtonRef.current
            ? cancelBookingButtonRef
            : duplicateButtonRef
        }
      />
      <CancelCollectiveBookingModal
        onDismiss={() => setIsCancelBookingModalOpen(false)}
        onValidate={cancelBooking}
        isFromOffer
        isDialogOpen={isCancelBookingModalOpen}
        refToFocusOnClose={
          archiveButtonRef.current ? archiveButtonRef : duplicateButtonRef
        }
      />
    </BasicLayout>
  )
}
