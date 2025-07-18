import {
  CollectiveOfferDisplayedStatus,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { getDateToFrenchText } from 'commons/utils/date'
import fullEditIcon from 'icons/full-edit.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
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

const isMoreThan48hAgo = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  return diffMs > 48 * 60 * 60 * 1000
}

export const BookableOfferTimeline = ({ offer }: BookableOfferTimeline) => {
  const { past, future } = offer.history

  const pastSteps = past.map(({ datetime, status }, index) => {
    const statusLabel = statusLabelMapping[status]
    const isCurrentStep = past.length - 1 === index

    if (status === CollectiveOfferDisplayedStatus.DRAFT) {
      return {
        type: TimelineStepType.WAITING,
        content: (
          <>
            <StatusWithDate status={statusLabel} />
            {isCurrentStep && (
              <Callout
                className={styles['callout']}
                variant={CalloutVariant.INFO}
                shouldShowIcon={false}
                links={[
                  {
                    icon: { src: fullEditIcon, alt: 'Modifier' },
                    href: `/offre/collectif/${offer.id}/creation`,
                    label: 'Reprendre mon brouillon',
                  },
                ]}
              >
                {
                  "Vous avez commencé à rédiger un brouillon. Vous pouvez le reprendre à tout moment afin de finaliser sa rédaction et l'envoyer à un établissement."
                }
              </Callout>
            )}
          </>
        ),
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
    const lastPastStep = past[past.length - 1]
    const lastPastStepStatus = lastPastStep.status

    if (
      waitingWording[lastPastStepStatus] &&
      lastPastStepStatus === CollectiveOfferDisplayedStatus.ENDED &&
      lastPastStep.datetime &&
      isMoreThan48hAgo(lastPastStep.datetime)
    ) {
      const waitingStep = {
        type: TimelineStepType.WAITING,
        content: <StatusWithDate status={waitingWording[lastPastStepStatus]} />,
      }
      return [...pastSteps, waitingStep, ...futureSteps]
    }

    if (
      waitingWording[lastPastStepStatus] &&
      lastPastStepStatus !== CollectiveOfferDisplayedStatus.ENDED
    ) {
      const waitingStep = {
        type: TimelineStepType.WAITING,
        content: <StatusWithDate status={waitingWording[lastPastStepStatus]} />,
      }
      return [...pastSteps, waitingStep, ...futureSteps]
    }
    return [...pastSteps, ...futureSteps]
  }

  return (
    <>
      <h2 className={styles['title']}>{"Suivi de l'offre"}</h2>
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
