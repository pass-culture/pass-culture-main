import {
  CollectiveOfferDisplayedStatus,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { getDateToFrenchText } from 'commons/utils/date'
import { Timeline, TimelineStepType } from 'ui-kit/Timeline/Timeline'

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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.PUBLISHED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
          />
        ),
      }
    }

    if (status === CollectiveOfferDisplayedStatus.ENDED) {
      return {
        type: TimelineStepType.SUCCESS,
        content: (
          <StatusWithDate
            status={statusLabel}
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
            date={datetime ? `Le ${getDateToFrenchText(datetime)}` : undefined}
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
    const lastPastStepStatus = past[past.length - 1].status

    // TODO gérer la step intermédiaire "en attente de remboursement" et ne l'afficher qu'après 48h post terminé
    if (waitingWording[lastPastStepStatus]) {
      const waitingStep = {
        type: TimelineStepType.WAITING,
        content: <StatusWithDate status={waitingWording[lastPastStepStatus]} />,
      }
      return [...pastSteps, waitingStep, ...futureSteps]
    }

    return [...pastSteps, ...futureSteps]
  }

  return (
    <div className={styles['container']}>
      <h2 className={styles['title']}>{"Suivi de l'offre"}</h2>
      <div className={styles['timeline-container']}>
        <Timeline steps={getAllSteps()} />
      </div>
    </div>
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
      <div className={styles['date']}>{date ?? null}</div>
    </div>
  )
}
