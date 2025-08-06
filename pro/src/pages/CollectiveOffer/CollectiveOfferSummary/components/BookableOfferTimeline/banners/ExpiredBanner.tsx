import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import fullEditIcon from '@/icons/full-edit.svg'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import { formatDateTime } from '../../CollectiveOfferSummary/components/utils/formatDatetime'
import styles from '../BookableOfferTimeline.module.scss'

export const ExpiredBanner = ({
  stepBeforeExpiredStatus,
  offerId,
  bookingLimitDatetime,
  departmentCode,
}: {
  stepBeforeExpiredStatus: CollectiveOfferDisplayedStatus
  offerId: number
  bookingLimitDatetime: string | null
  departmentCode?: string | null
  contactEmail?: string | null
}) => {
  const hasPublished =
    stepBeforeExpiredStatus === CollectiveOfferDisplayedStatus.PUBLISHED

  const message = hasPublished
    ? 'L’enseignant n’a pas préréservé l’offre avant la date limite de réservation fixée au '
    : 'Le chef d’établissement n’a pas réservé l’offre avant la date limite de réservation fixée au '

  return (
    <Callout
      title=""
      testId="callout-booking-expired"
      className={styles['callout']}
      variant={CalloutVariant.ERROR}
      links={[
        {
          label: 'Modifier la date limite de réservation',
          icon: { src: fullEditIcon, alt: 'Modifier' },
          href: `/offre/${offerId}/collectif/stocks/edition`,
        },
      ]}
    >
      <div>
        {message}
        <span className={styles['callout-accent']}>
          {formatDateTime(
            bookingLimitDatetime ?? '',
            FORMAT_DD_MM_YYYY,
            departmentCode
          )}
          .
        </span>
        <div className={styles['callout-space']}></div>
        <span>
          Pour qu’il puisse {hasPublished ? 'préréserver' : 'réserver'} à
          nouveau, vous pouvez modifier la date limite de réservation, ce qui
          rendra automatiquement la{' '}
          {hasPublished ? 'préréservation' : 'réservation'} disponible auprès de
          l’enseignant.
        </span>
      </div>
    </Callout>
  )
}
