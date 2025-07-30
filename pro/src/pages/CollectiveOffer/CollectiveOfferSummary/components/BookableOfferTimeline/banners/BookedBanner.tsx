import { isBefore } from 'date-fns'

import { FORMAT_DD_MM_YYYY } from 'commons/utils/date'
import fullEditIcon from 'icons/full-edit.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import { formatDateTime } from '../../CollectiveOfferSummary/components/utils/formatDatetime'
import styles from '../BookableOfferTimeline.module.scss'

interface BookedBannerProps {
  offerId: number
  cancellationLimitDate: string | undefined
  canEditDiscount: boolean
  departmentCode?: string | null
}

export const BookedBanner = ({
  offerId,
  cancellationLimitDate,
  canEditDiscount,
  departmentCode,
}: BookedBannerProps) => {
  if (!cancellationLimitDate) {
    return null
  }

  const isCancellationLimitDateInPast = isBefore(
    new Date(cancellationLimitDate),
    new Date()
  )

  return (
    <Callout
      title=""
      testId="callout-booking-booked"
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={
        canEditDiscount
          ? [
              {
                label: 'Modifier à la baisse le prix ou le nombre d’élèves',
                icon: { src: fullEditIcon, alt: 'Modifier' },
                href: `/offre/${offerId}/collectif/stocks/edition`,
              },
            ]
          : []
      }
    >
      <div>
        {isCancellationLimitDateInPast ? (
          <>
            La réservation n’est plus annulable par l’établissement scolaire. De
            votre côté, vous pouvez annuler la réservation ou modifier à la
            baisse le prix ou le nombre de participants jusqu’à 48 heures après
            la date de l’évènement.
          </>
        ) : (
          <>
            Le chef d’établissement a confirmé la préréservation de l’offre. À
            partir du{' '}
            {formatDateTime(
              cancellationLimitDate,
              FORMAT_DD_MM_YYYY,
              departmentCode
            )}
            , la réservation ne sera plus annulable par l’établissement
            scolaire.
            <br />
            De votre côté, vous pouvez annuler la réservation et modifier le
            prix ou le nombre d’élève à la baisse jusqu’à 48 heures après la
            date de l’évènement.
          </>
        )}
      </div>
    </Callout>
  )
}
