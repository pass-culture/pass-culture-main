import type { ReactNode } from 'react'

import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { FORMAT_DD_MMMM_YYYY } from '@/commons/utils/date'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { Timeline, TimelineStepType } from '@/ui-kit/Timeline/Timeline'

import { formatDateTime } from '../CollectiveOfferSummary/components/utils/formatDatetime'
import styles from './BookableOfferTimeline.module.scss'
import { ArchivedBanner } from './banners/ArchivedBanner'
import { BookedBanner } from './banners/BookedBanner'
import { BookingWaitingBanner } from './banners/BookingWaitingBanner'
import { CancelledBanner } from './banners/CancelledBanner'
import { DraftBanner } from './banners/DraftBanner'
import { EndBanner } from './banners/EndBanner'
import { ExpiredBanner } from './banners/ExpiredBanner'
import { ReimbursedBanner } from './banners/ReimbursedBanner'
import { ReimbursementWaitingBanner } from './banners/ReimbursementWaitingBanner'
import { RejectedBanner } from './banners/RejectedBanner'
import { UnderReviewBanner } from './banners/UnderReviewBanner'

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

const getDateTimeLabel = (
  datetime: string | null | undefined,
  venueDepartmentCode: string | null | undefined
) => {
  return datetime
    ? `Le ${formatDateTime(datetime, FORMAT_DD_MMMM_YYYY, venueDepartmentCode)}`
    : undefined
}

const waitingWording: Partial<Record<CollectiveOfferDisplayedStatus, string>> =
  {
    [CollectiveOfferDisplayedStatus.PUBLISHED]: 'En attente de préréservation',
    [CollectiveOfferDisplayedStatus.PREBOOKED]: 'En attente de réservation',
    [CollectiveOfferDisplayedStatus.ENDED]: 'En attente de remboursement',
  }

type TimelineStep = {
  type: TimelineStepType
  content: ReactNode
}

type PastHistoryStep =
  GetCollectiveOfferResponseModel['history']['past'][number]

const getStatusWithDate = (
  status: CollectiveOfferDisplayedStatus,
  datetime: string | null | undefined,
  venueDepartmentCode: string | null | undefined
) => {
  return (
    <StatusWithDate
      status={statusLabelMapping[status]}
      date={getDateTimeLabel(datetime, venueDepartmentCode)}
    />
  )
}

const buildFallbackPastStep = (
  status: CollectiveOfferDisplayedStatus
): TimelineStep => {
  return {
    type: TimelineStepType.SUCCESS,
    content: statusLabelMapping[status],
  }
}

const buildWaitingPastStep = ({
  offer,
  status,
  isCurrentStep,
}: {
  offer: GetCollectiveOfferResponseModel
  status: CollectiveOfferDisplayedStatus
  isCurrentStep: boolean
}): TimelineStep => {
  return {
    type: TimelineStepType.WAITING,
    content: (
      <>
        <StatusWithDate status={statusLabelMapping[status]} />
        {isCurrentStep && status === CollectiveOfferDisplayedStatus.DRAFT && (
          <DraftBanner offerId={offer.id} />
        )}
        {isCurrentStep &&
          status === CollectiveOfferDisplayedStatus.UNDER_REVIEW && (
            <UnderReviewBanner />
          )}
      </>
    ),
  }
}

const buildRejectedPastStep = ({
  offer,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
}: {
  offer: GetCollectiveOfferResponseModel
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  return {
    type: TimelineStepType.ERROR,
    content: (
      <>
        {getStatusWithDate(
          CollectiveOfferDisplayedStatus.REJECTED,
          datetime,
          venueDepartmentCode
        )}
        {isCurrentStep && (
          <RejectedBanner
            offerId={offer.id}
            canDuplicate={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_DUPLICATE
            )}
          />
        )}
      </>
    ),
  }
}

const buildBookedPastStep = ({
  offer,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
}: {
  offer: GetCollectiveOfferResponseModel
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  return {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        {getStatusWithDate(
          CollectiveOfferDisplayedStatus.BOOKED,
          datetime,
          venueDepartmentCode
        )}
        {isCurrentStep && (
          <BookedBanner
            offerId={offer.id}
            cancellationLimitDate={offer.booking?.cancellationLimitDate}
            departmentCode={offer.venue.departementCode}
            canEditDiscount={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
            )}
          />
        )}
      </>
    ),
  }
}

const buildExpiredPastStep = ({
  offer,
  past,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
  bookingLimitDatetime,
}: {
  offer: GetCollectiveOfferResponseModel
  past: PastHistoryStep[]
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
  bookingLimitDatetime: string
}): TimelineStep => {
  const stepBeforeExpiredStatus = past[past.length - 2].status

  return {
    type: TimelineStepType.ERROR,
    content: (
      <>
        {getStatusWithDate(
          CollectiveOfferDisplayedStatus.EXPIRED,
          datetime,
          venueDepartmentCode
        )}
        {isCurrentStep && (
          <ExpiredBanner
            stepBeforeExpiredStatus={stepBeforeExpiredStatus}
            offerId={offer.id}
            bookingLimitDatetime={bookingLimitDatetime}
            departmentCode={offer.venue.departementCode}
            canEditDates={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_EDIT_DATES
            )}
            contactEmail={
              offer.booking?.educationalRedactor?.email ?? offer.teacher?.email
            }
          />
        )}
      </>
    ),
  }
}

const buildCancelledPastStep = ({
  offer,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
}: {
  offer: GetCollectiveOfferResponseModel
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  return {
    type: TimelineStepType.ERROR,
    content: (
      <>
        {getStatusWithDate(
          CollectiveOfferDisplayedStatus.CANCELLED,
          datetime,
          venueDepartmentCode
        )}
        {isCurrentStep && (
          <CancelledBanner
            offerId={offer.id}
            reason={offer.booking?.cancellationReason}
            canDuplicate={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_DUPLICATE
            )}
          />
        )}
      </>
    ),
  }
}

const buildEndedPastStep = ({
  offer,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
}: {
  offer: GetCollectiveOfferResponseModel
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  const endedMoreThan48hAgo = datetime && isMoreThan48hAgo(datetime)

  return {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        {getStatusWithDate(
          CollectiveOfferDisplayedStatus.ENDED,
          datetime,
          venueDepartmentCode
        )}
        {isCurrentStep && !endedMoreThan48hAgo && (
          <EndBanner
            offerId={offer.id}
            canEditDiscount={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
            )}
          />
        )}
      </>
    ),
  }
}

const buildSimpleSuccessPastStep = ({
  status,
  datetime,
  isCurrentStep,
  venueDepartmentCode,
}: {
  status:
    | CollectiveOfferDisplayedStatus.REIMBURSED
    | CollectiveOfferDisplayedStatus.ARCHIVED
  datetime: string | null | undefined
  isCurrentStep: boolean
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  return {
    type: TimelineStepType.SUCCESS,
    content: (
      <>
        {getStatusWithDate(status, datetime, venueDepartmentCode)}
        {isCurrentStep &&
          status === CollectiveOfferDisplayedStatus.REIMBURSED && (
            <ReimbursedBanner />
          )}
        {isCurrentStep &&
          status === CollectiveOfferDisplayedStatus.ARCHIVED && (
            <ArchivedBanner />
          )}
      </>
    ),
  }
}

const buildPastStep = ({
  offer,
  past,
  datetime,
  status,
  index,
  venueDepartmentCode,
}: {
  offer: GetCollectiveOfferResponseModel
  past: PastHistoryStep[]
  datetime: string | null | undefined
  status: CollectiveOfferDisplayedStatus
  index: number
  venueDepartmentCode: string | null | undefined
}): TimelineStep => {
  const isCurrentStep = past.length - 1 === index

  switch (status) {
    case CollectiveOfferDisplayedStatus.DRAFT:
    case CollectiveOfferDisplayedStatus.UNDER_REVIEW:
      return buildWaitingPastStep({
        offer,
        status,
        isCurrentStep,
      })
    case CollectiveOfferDisplayedStatus.REJECTED:
      return buildRejectedPastStep({
        offer,
        datetime,
        isCurrentStep,
        venueDepartmentCode,
      })
    case CollectiveOfferDisplayedStatus.PUBLISHED:
    case CollectiveOfferDisplayedStatus.PREBOOKED:
      return {
        type: TimelineStepType.SUCCESS,
        content: getStatusWithDate(status, datetime, venueDepartmentCode),
      }
    case CollectiveOfferDisplayedStatus.BOOKED:
      return buildBookedPastStep({
        offer,
        datetime,
        isCurrentStep,
        venueDepartmentCode,
      })
    case CollectiveOfferDisplayedStatus.EXPIRED:
      return offer.collectiveStock?.bookingLimitDatetime
        ? buildExpiredPastStep({
            offer,
            past,
            datetime,
            isCurrentStep,
            venueDepartmentCode,
            bookingLimitDatetime: offer.collectiveStock.bookingLimitDatetime,
          })
        : buildFallbackPastStep(status)
    case CollectiveOfferDisplayedStatus.CANCELLED:
      return buildCancelledPastStep({
        offer,
        datetime,
        isCurrentStep,
        venueDepartmentCode,
      })
    case CollectiveOfferDisplayedStatus.ENDED:
      return buildEndedPastStep({
        offer,
        datetime,
        isCurrentStep,
        venueDepartmentCode,
      })
    case CollectiveOfferDisplayedStatus.REIMBURSED:
    case CollectiveOfferDisplayedStatus.ARCHIVED:
      return buildSimpleSuccessPastStep({
        status,
        datetime,
        isCurrentStep,
        venueDepartmentCode,
      })
    default:
      return buildFallbackPastStep(status)
  }
}

const buildFutureStep = (
  status: CollectiveOfferDisplayedStatus
): TimelineStep => {
  return {
    type: TimelineStepType.DISABLED,
    content: (
      <StatusWithDate
        status={statusLabelMapping[status]}
        stepType={TimelineStepType.DISABLED}
      />
    ),
  }
}

const getWaitingStep = (
  offer: GetCollectiveOfferResponseModel,
  lastPastStep: PastHistoryStep
): TimelineStep | null => {
  const lastPastStepStatus = lastPastStep.status

  if (!waitingWording[lastPastStepStatus]) {
    return null
  }

  if (
    lastPastStepStatus === CollectiveOfferDisplayedStatus.ENDED &&
    lastPastStep.datetime &&
    isMoreThan48hAgo(lastPastStep.datetime)
  ) {
    return {
      type: TimelineStepType.WAITING,
      content: (
        <>
          <StatusWithDate status={waitingWording[lastPastStepStatus]} />
          <ReimbursementWaitingBanner />
        </>
      ),
    }
  }

  if (
    (lastPastStepStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
      lastPastStepStatus === CollectiveOfferDisplayedStatus.PREBOOKED) &&
    offer.collectiveStock?.bookingLimitDatetime
  ) {
    return {
      type: TimelineStepType.WAITING,
      content: (
        <>
          <StatusWithDate status={waitingWording[lastPastStepStatus]} />
          <BookingWaitingBanner
            offerStatus={lastPastStepStatus}
            offerId={offer.id}
            bookingLimitDatetime={offer.collectiveStock.bookingLimitDatetime}
            departmentCode={offer.venue.departementCode}
            canEditDates={isActionAllowedOnCollectiveOffer(
              offer,
              CollectiveOfferAllowedAction.CAN_EDIT_DATES
            )}
            contactEmail={
              offer.booking?.educationalRedactor?.email ?? offer.teacher?.email
            }
          />
        </>
      ),
    }
  }

  return null
}

const buildAllSteps = ({
  offer,
  past,
  pastSteps,
  futureSteps,
}: {
  offer: GetCollectiveOfferResponseModel
  past: PastHistoryStep[]
  pastSteps: TimelineStep[]
  futureSteps: TimelineStep[]
}) => {
  const lastPastStep = past[past.length - 1]
  const waitingStep = getWaitingStep(offer, lastPastStep)

  if (waitingStep) {
    return [...pastSteps, waitingStep, ...futureSteps]
  }

  return [...pastSteps, ...futureSteps]
}

export const BookableOfferTimeline = ({ offer }: BookableOfferTimeline) => {
  const { past, future } = offer.history

  const venueDepartmentCode =
    offer.location?.location?.departmentCode ?? offer.venue.departementCode

  const pastSteps = past.map(({ datetime, status }, index) =>
    buildPastStep({
      offer,
      past,
      datetime,
      status,
      index,
      venueDepartmentCode,
    })
  )
  const futureSteps = future.map(buildFutureStep)
  const allSteps = buildAllSteps({ offer, past, pastSteps, futureSteps })

  return (
    <>
      <h2 className={styles['title']}>{'Suivi de l’offre'}</h2>
      <div className={styles['timeline-container']}>
        <Timeline steps={allSteps} />
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
