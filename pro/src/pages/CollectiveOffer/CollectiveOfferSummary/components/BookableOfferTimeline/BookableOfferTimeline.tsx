import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { FORMAT_DD_MMMM_YYYY } from 'commons/utils/date'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { Timeline, TimelineStepType } from 'ui-kit/Timeline/Timeline'

import { formatDateTime } from '../CollectiveOfferSummary/components/utils/formatDatetime'

import { ArchivedBanner } from './banners/ArchivedBanner'
import { BookedBanner } from './banners/BookedBanner'
import { BookingWaitingBanner } from './banners/BookingWaitingBanner'
import { CancelledBanner } from './banners/CancelledBanner'
import { DraftBanner } from './banners/DraftBanner'
import { ExpiredBanner } from './banners/ExpiredBanner'
import { ReimbursedBanner } from './banners/ReimbursedBanner'
import { RejectedBanner } from './banners/RejectedBanner'
import { UnderReviewBanner } from './banners/UnderReviewBanner'
import styles from './BookableOfferTimeline.module.scss'

type BookableOfferTimeline = {
  offer: GetCollectiveOfferResponseModel
}

const statusLabelMapping = {
  [CollectiveOfferDisplayedStatus.PUBLISHED]: 'Publiée',
  [CollectiveOfferDisplayedStatus.UNDER_REVIEW]: 'En instruction',
  [CollectiveOfferDisplayedStatus.REJECTED]: 'Non conforme',
  [CollectiveOfferDisplayedStatus.PREBOOKED]: 'Préréservée',
  [CollectiveOfferDisplayedStatus.BOOKED]: 'Réservée',
  [CollectiveOfferDisplayedStatus.EXPIRED]: 'Expirée',
  [CollectiveOfferDisplayedStatus.ENDED]: 'Terminée',
  [CollectiveOfferDisplayedStatus.CANCELLED]: 'Annulée',
  [CollectiveOfferDisplayedStatus.REIMBURSED]: 'Remboursée',
  [CollectiveOfferDisplayedStatus.ARCHIVED]: 'Archivée',
  [CollectiveOfferDisplayedStatus.DRAFT]: 'Brouillon',
  [CollectiveOfferDisplayedStatus.HIDDEN]: 'En pause',
}

const isMoreThan48hAgo = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  return diffMs > 48 * 60 * 60 * 1000
}

export const BookableOfferTimeline = ({ offer }: BookableOfferTimeline) => {
  const { past, future } = offer.history

  const venueDepartmentCode =
    offer.location?.address?.departmentCode ?? offer.venue.departementCode

  const pastSteps = past.map(({ datetime, status }, index) => {
    const statusLabel = statusLabelMapping[status]
    const isCurrentStep = past.length - 1 === index

    if (status === CollectiveOfferDisplayedStatus.DRAFT) {
      return {
        type: TimelineStepType.WAITING,
        content: (
          <>
            <StatusWithDate status={statusLabel} />
            {isCurrentStep && <DraftBanner offerId={offer.id} />}
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.UNDER_REVIEW) {
      return {
        type: TimelineStepType.WAITING,
        content: (
          <>
            <StatusWithDate status={statusLabel} />
            {isCurrentStep && <UnderReviewBanner />}
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.REJECTED) {
      return {
        type: TimelineStepType.ERROR,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            {isCurrentStep && <RejectedBanner offerId={offer.id} />}
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.PUBLISHED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.PREBOOKED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.BOOKED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            <BookedBanner
              offerId={offer.id}
              cancellationLimitDate={offer.booking?.cancellationLimitDate}
              departmentCode={offer.venue.departementCode}
              canEditDiscount={isActionAllowedOnCollectiveOffer(
                offer,
                CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
              )}
            />
          </>
        ),
      }
    }

    if (
      status === CollectiveOfferDisplayedStatus.EXPIRED &&
      offer.collectiveStock?.bookingLimitDatetime
    ) {
      const stepBeforeExpiredStatus = past[past.length - 2].status

      return {
        type: TimelineStepType.ERROR,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            <ExpiredBanner
              stepBeforeExpiredStatus={stepBeforeExpiredStatus}
              offerId={offer.id}
              bookingLimitDatetime={offer.collectiveStock.bookingLimitDatetime}
              departmentCode={offer.venue.departementCode}
              contactEmail={
                offer.booking?.educationalRedactor?.email ??
                offer.teacher?.email
              }
            />
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.CANCELLED) {
      return {
        type: TimelineStepType.ERROR,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            {isCurrentStep && (
              <CancelledBanner
                offerId={offer.id}
                reason={offer.booking?.cancellationReason}
              />
            )}
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.ENDED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.REIMBURSED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            {isCurrentStep && <ReimbursedBanner />}
          </>
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.ARCHIVED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <>
            <StatusWithDate
              status={statusLabel}
              date={
                datetime
                  ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
                  : undefined
              }
            />
            {isCurrentStep && <ArchivedBanner />}
          </>
        ),
      }
    }

    return {
      type: TimelineStepType.SUCCESS,
      content: statusLabelMapping[status],
    }
  })

  const futureSteps = future.map((status) => {
    return {
      type: TimelineStepType.DISABLED,
      content: (
        <StatusWithDate
          status={statusLabelMapping[status]}
          stepType={TimelineStepType.DISABLED}
        />
      ),
    }
  })

  const waitingWording: Partial<
    Record<CollectiveOfferDisplayedStatus, string>
  > = {
    [CollectiveOfferDisplayedStatus.PUBLISHED]: 'En attente de préréservation',
    [CollectiveOfferDisplayedStatus.PREBOOKED]: 'En attente de réservation',
    [CollectiveOfferDisplayedStatus.ENDED]: 'En attente de remboursement',
  }

  const getAllSteps = () => {
    const lastPastStep = past[past.length - 1]
    const lastPastStepStatus = lastPastStep.status

    if (waitingWording[lastPastStepStatus]) {
      if (
        lastPastStepStatus === CollectiveOfferDisplayedStatus.ENDED &&
        lastPastStep.datetime &&
        isMoreThan48hAgo(lastPastStep.datetime)
      ) {
        const waitingStep = {
          type: TimelineStepType.WAITING,
          content: (
            <StatusWithDate status={waitingWording[lastPastStepStatus]} />
          ),
        }
        return [...pastSteps, waitingStep, ...futureSteps]
      }

      if (
        (lastPastStepStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
          lastPastStepStatus === CollectiveOfferDisplayedStatus.PREBOOKED) &&
        offer.collectiveStock?.bookingLimitDatetime
      ) {
        const waitingStep = {
          type: TimelineStepType.WAITING,
          content: (
            <>
              <StatusWithDate status={waitingWording[lastPastStepStatus]} />
              <BookingWaitingBanner
                offerStatus={lastPastStepStatus}
                offerId={offer.id}
                bookingLimitDatetime={
                  offer.collectiveStock.bookingLimitDatetime
                }
                departmentCode={offer.venue.departementCode}
                contactEmail={
                  offer.booking?.educationalRedactor?.email ??
                  offer.teacher?.email
                }
              />
            </>
          ),
        }

        return [...pastSteps, waitingStep, ...futureSteps]
      }
    }

    return [...pastSteps, ...futureSteps]
  }

  return (
    <>
      <h2 className={styles['title']}>{'Suivi de l’offre'}</h2>
      <div className={styles['timeline-container']}>
        <Timeline steps={getAllSteps()} />
      </div>
    </>
  )
}

const StatusWithDate = ({
  status,
  stepType,
  date,
}: {
  status: string
  stepType?: TimelineStepType
  date?: string | null
}) => {
  return (
    <div className={styles['status']}>
      <div
        className={
          stepType === TimelineStepType.DISABLED
            ? styles['status-label-disabled']
            : styles['status-label']
        }
      >
        {status}
      </div>
      {date && <div className={styles['date']}>{date}</div>}
    </div>
  )
}
