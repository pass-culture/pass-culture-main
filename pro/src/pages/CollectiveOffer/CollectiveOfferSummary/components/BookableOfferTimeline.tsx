import {
  CollectiveOfferDisplayedStatus,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY } from 'commons/utils/date'
import { Timeline, TimelineStepType } from 'ui-kit/Timeline/Timeline'

import styles from './BookableOfferTimeline.module.scss'
import { formatDateTime } from './CollectiveOfferSummary/components/utils/formatDatetime'

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

export const BookableOfferTimeline = ({ offer }: BookableOfferTimeline) => {
  const { past, future } = offer.history

  const pastSteps = past.map(({ datetime, status }) => {
    const statusLabel = statusLabelMapping[status]

    if (status === CollectiveOfferDisplayedStatus.DRAFT) {
      return {
        type: TimelineStepType.WAITING,
        content: <StatusWithDate status={statusLabel} />,
      }
    }

    if (status === CollectiveOfferDisplayedStatus.UNDER_REVIEW) {
      return {
        type: TimelineStepType.WAITING,
        content: <StatusWithDate status={statusLabel} />,
      }
    }

    if (status === CollectiveOfferDisplayedStatus.REJECTED) {
      return {
        type: TimelineStepType.ERROR,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    // TODO : ici ajouter la step intermédiaire "en attente de préréservation"
    if (status === CollectiveOfferDisplayedStatus.PUBLISHED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    // TODO : ici ajouter la step intermédiaire "en attente de réservation"
    if (status === CollectiveOfferDisplayedStatus.PREBOOKED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
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
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.EXPIRED) {
      return {
        type: TimelineStepType.ERROR,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.CANCELLED) {
      return {
        type: TimelineStepType.ERROR,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    // TODO ajouter la step intermédiaire "en attente de remboursement" (attention à la règle d'affichage <48h)
    if (status === CollectiveOfferDisplayedStatus.ENDED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
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
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.ARCHIVED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={
              datetime
                ? `Le ${formatDateTime(datetime, FORMAT_DD_MM_YYYY)}`
                : undefined
            }
          />
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
      content: statusLabelMapping[status],
    }
  })

  return <Timeline steps={[...pastSteps, ...futureSteps]} />
}

const StatusWithDate = ({
  status,
  date,
}: {
  status: string
  date?: string
}) => {
  return (
    <div className={styles['status']}>
      <div className={styles['status-label']}>{status}</div>
      <div>{date ?? null}</div>
    </div>
  )
}
