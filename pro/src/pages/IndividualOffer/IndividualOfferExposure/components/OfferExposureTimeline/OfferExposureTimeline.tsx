import cn from 'classnames'
import type { JSX } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type ExposureEventResponseModel,
  ExposureEventType,
} from '@/apiClient/v1'
import { GET_OFFER_EXPOSURE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { FORMAT_DD_MM } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import fullIncrease from '@/icons/full-increase.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Timeline, TimelineStepType } from '@/ui-kit/Timeline/Timeline'

import { isOngoing } from '../../commons/utils'
import styles from './OfferExposureTimeline.module.scss'

type OfferExposureTimelineProps = {
  offerId: number
  creationDate: string
  departmentCode: string
}

const getEventTitle = (event: ExposureEventResponseModel): string => {
  switch (event.type) {
    case ExposureEventType.HEADLINE:
      return 'Mise à la une de votre offre'
    case ExposureEventType.HIGHLIGHT:
      return `Lien de votre offre au temps fort “${event.name}”`
    case ExposureEventType.PRO_ADVICE:
      return 'Ajout d’une recommandation'
    default:
      return ''
  }
}

const getEventDates = (
  event: ExposureEventResponseModel,
  departmentCode: string
): string => {
  const startLabel = formatLocalTimeDateString(
    event.startDate,
    departmentCode,
    FORMAT_DD_MM
  )

  // The end date is only displayed once the enhancement is finished.
  if (event.endDate && !isOngoing(event)) {
    return `${startLabel} - ${formatLocalTimeDateString(event.endDate, departmentCode, FORMAT_DD_MM)}`
  }

  return startLabel
}

// An ongoing enhancement is shown as "waiting", a finished one as "disabled".
const getStepType = (event: ExposureEventResponseModel): TimelineStepType => {
  return isOngoing(event) ? TimelineStepType.WAITING : TimelineStepType.DISABLED
}

export const OfferExposureTimeline = ({
  offerId,
  creationDate,
  departmentCode,
}: OfferExposureTimelineProps): JSX.Element | null => {
  const { data: exposure } = useSWR(
    [GET_OFFER_EXPOSURE_QUERY_KEY, offerId],
    () => api.getOfferExposure({ path: { offer_id: offerId } })
  )

  const events = exposure?.events ?? []

  if (events.length === 0) {
    return null
  }

  const steps = events.map((event) => {
    const type = getStepType(event)

    return {
      type,
      content: (
        <div
          className={cn(styles['event'], {
            [styles['event-waiting']]: type === TimelineStepType.WAITING,
            [styles['event-disabled']]: type === TimelineStepType.DISABLED,
          })}
        >
          <p className={styles['event-title']}>
            {getEventDates(event, departmentCode)} : {getEventTitle(event)}
          </p>
          {type === TimelineStepType.DISABLED && !!event.viewsOnPeriod && (
            <p className={styles['event-views']}>
              <SvgIcon
                src={fullIncrease}
                alt=""
                width="16"
                className={styles['event-views-icon']}
              />
              +{event.viewsOnPeriod}{' '}
              {pluralizeFr(
                event.viewsOnPeriod,
                'consultation',
                'consultations'
              )}{' '}
              sur cette période
            </p>
          )}
        </div>
      ),
    }
  })

  // When there are fewer than 3 steps, we close the timeline with the offer creation step
  if (events.length < 3) {
    steps.push({
      type: TimelineStepType.WAITING,
      content: (
        <div className={cn(styles['event'], [styles['event-waiting']])}>
          <p className={styles['event-title']}>
            {formatLocalTimeDateString(
              creationDate,
              departmentCode,
              FORMAT_DD_MM
            )}{' '}
            : Création de votre offre
          </p>
        </div>
      ),
    })
  }

  return (
    <section className={styles['timeline']}>
      <h2 className={styles['title']}>Vos dernières actions</h2>
      <Timeline steps={steps} />
    </section>
  )
}
