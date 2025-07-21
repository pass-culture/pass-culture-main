import { differenceInCalendarDays } from 'date-fns'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY } from 'commons/utils/date'
import { pluralize } from 'commons/utils/pluralize'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullEditIcon from 'icons/full-edit.svg'
import fullMailIcon from 'icons/full-mail.svg'
import fullWarningIcon from 'icons/full-warning.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import { formatDateTime } from '../../CollectiveOfferSummary/components/utils/formatDatetime'
import styles from '../BookableOfferTimeline.module.scss'

export const BookingWaitingBanner = ({
  offerStatus,
  offerId,
  bookingLimitDatetime,
  departmentCode,
  contactEmail,
}: {
  offerStatus:
    | CollectiveOfferDisplayedStatus.PUBLISHED
    | CollectiveOfferDisplayedStatus.PREBOOKED
  offerId: number
  bookingLimitDatetime: string
  departmentCode?: string | null
  contactEmail?: string | null
}) => {
  const daysCountBeforeExpiration = differenceInCalendarDays(
    new Date(bookingLimitDatetime),
    new Date()
  )

  const isExpiringSoon = daysCountBeforeExpiration <= 7

  return (
    <Callout
      testId="callout-booking-waiting"
      className={styles['callout']}
      shouldShowIcon={false}
      variant={isExpiringSoon ? CalloutVariant.WARNING : CalloutVariant.INFO}
      links={[
        {
          label: 'Modifier la date limite de réservation',
          icon: { src: fullEditIcon, alt: 'Modifier' },
          href: `/offre/${offerId}/collectif/stocks/edition`,
        },
        ...(contactEmail && isExpiringSoon
          ? [
              {
                label: "Contacter l'établissement",
                icon: { src: fullMailIcon, alt: "Contacter l'établissement" },
                href: `mailto:${contactEmail}`,
                isExternal: true,
              },
            ]
          : []),
      ]}
    >
      <>
        {isExpiringSoon && (
          <Tag
            variant={TagVariant.WARNING}
            icon={fullWarningIcon}
            label={`expire ${
              daysCountBeforeExpiration > 0
                ? `dans ${pluralize(daysCountBeforeExpiration, 'jour')}`
                : 'aujourd’hui'
            }`}
          />
        )}
        <div>
          {offerStatus === CollectiveOfferDisplayedStatus.PUBLISHED
            ? "L'enseignant doit impérativement préréserver l'offre avant le "
            : "Le chef d'établissement doit impérativement confirmer la préréservation de l'offre avant le "}
          <span className={styles['callout-accent']}>
            {formatDateTime(
              bookingLimitDatetime,
              FORMAT_DD_MM_YYYY,
              departmentCode
            )}
          </span>
          . Sinon, elle sera automatiquement annulée et vous ne pourrez pas en
          obtenir le remboursement par la suite.
        </div>
      </>
    </Callout>
  )
}
