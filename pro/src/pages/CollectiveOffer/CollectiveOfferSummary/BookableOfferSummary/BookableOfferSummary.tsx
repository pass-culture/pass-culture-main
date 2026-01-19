import cn from 'classnames'
import { useRef, useState } from 'react'
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
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  selectCurrentOfferer,
  selectCurrentOffererId,
} from '@/commons/store/offerer/selectors'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import {
  isActionAllowedOnCollectiveOffer,
  isCollectiveOfferEditable,
} from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { CancelCollectiveBookingModal } from '@/components/CancelCollectiveBookingModal/CancelCollectiveBookingModal'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { EducationalInstitutionDetails } from '@/components/EducationalInstitutionDetails/EducationalInstitutionDetails'
import { SynchronizedProviderInformation } from '@/components/SynchronisedProviderInformation/SynchronizedProviderInformation'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
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
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { DetailItem } from '../components/DetailItem/DetailItem'
import styles from './BookableOfferSummary.module.scss'

export type BookableOfferSummaryProps = {
  offer: GetCollectiveOfferResponseModel
}

export const BookableOfferSummary = ({ offer }: BookableOfferSummaryProps) => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const offerer = useAppSelector(selectCurrentOfferer)

  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const duplicateButtonRef = useRef<HTMLButtonElement>(null)
  const adagePreviewButtonRef = useRef<HTMLAnchorElement>(null)
  const cancelBookingButtonRef = useRef<HTMLButtonElement>(null)

  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false)
  const [isCancelBookingModalOpen, setIsCancelBookingModalOpen] =
    useState(false)

  const cancelBooking = async () => {
    if (!offer.id) {
      snackBar.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.cancelCollectiveOfferBooking(offer.id)
      await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])
      setIsCancelBookingModalOpen(false)
      snackBar.success(
        'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
      )
    } catch {
      snackBar.error(
        'Une erreur est survenue lors de l’annulation de la réservation.'
      )
    }
  }

  const formatDateRangeWithTime = (): string => {
    const { startDatetime, endDatetime } = offer.collectiveStock || {}
    const venueDepartmentCode =
      offer.location?.location?.departmentCode ?? offer.venue.departementCode

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
      snackBar.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.patchCollectiveOffersArchive({ ids: [offer.id] })
      await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])

      setIsArchiveModalOpen(false)

      snackBar.success('L’offre a bien été archivée')
    } catch {
      snackBar.error('Une erreur est survenue lors de l’archivage de l’offre')
    }
  }

  const canEditOffer = isCollectiveOfferEditable(offer)

  const canArchiveOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_ARCHIVE
  )

  const canDuplicateOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_DUPLICATE
  )

  const canPreviewOffer =
    offer.displayedStatus !== CollectiveOfferDisplayedStatus.DRAFT &&
    offer.displayedStatus !== CollectiveOfferDisplayedStatus.ARCHIVED

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
      {offer.provider?.name && (
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
            <DetailItem alt={offer.venue.publicName} src={strokeHomeIcon}>
              Proposé par {offer.venue.publicName}
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
                ? `${offer.collectiveStock.numberOfTickets} ${pluralizeFr(offer.collectiveStock.numberOfTickets, 'participant', 'participants')}`
                : DEFAULT_RECAP_VALUE}
            </DetailItem>
            <DetailItem alt="Prix de l’offre" src={strokeEuroIcon}>
              {offer.collectiveStock?.price ||
              offer.collectiveStock?.price === 0
                ? `${offer.collectiveStock.price} ${pluralizeFr(offer.collectiveStock.price, 'euro', 'euros')}`
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
                  <Button
                    as="a"
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                    size={ButtonSize.SMALL}
                    to={draftOfferLink ? draftOfferLink : offerEditLink}
                    aria-label={'Modifier l’offre'}
                    icon={fullEditIcon}
                    label="Modifier"
                  />
                </li>
              )}

              {canPreviewOffer && (
                <li>
                  <Button
                    as="a"
                    to={`/offre/${offer.id}/collectif/apercu`}
                    icon={fullShowIcon}
                    ref={adagePreviewButtonRef}
                    label="Aperçu"
                  />
                </li>
              )}

              {canDuplicateOffer && (
                <li>
                  <Button
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    icon={fullCopyIcon}
                    onClick={async () => {
                      logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
                        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_RECAP,
                        offererId: selectedOffererId?.toString(),
                        offerId: offer.id,
                        offerStatus: offer.displayedStatus,
                        offerType: 'collective',
                      })
                      await duplicateBookableOffer(navigate, snackBar, offer.id)
                    }}
                    ref={duplicateButtonRef}
                    label="Dupliquer"
                  />
                </li>
              )}
              {canArchiveOffer && (
                <li>
                  <Button
                    onClick={() => setIsArchiveModalOpen(true)}
                    icon={fullArchiveIcon}
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    ref={archiveButtonRef}
                    label="Archiver"
                  />
                </li>
              )}
              {isBookingCancellable && (
                <li>
                  <Button
                    icon={fullClearIcon}
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    onClick={() => setIsCancelBookingModalOpen(true)}
                    ref={cancelBookingButtonRef}
                    label="Annuler la réservation"
                  />
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

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button
            as="a"
            to={computeCollectiveOffersUrl({})}
            label="Retour à la liste des offres"
          />
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </BasicLayout>
  )
}
