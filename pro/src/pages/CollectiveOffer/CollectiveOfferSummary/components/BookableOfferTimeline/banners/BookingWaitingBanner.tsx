import { differenceInCalendarDays } from 'date-fns'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { getExpirationText } from '@/commons/core/OfferEducational/utils/getExpirationText'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import {
  Banner,
  type BannerLink,
  BannerVariants,
} from '@/design-system/Banner/Banner'
import fullEditIcon from '@/icons/full-edit.svg'
import fullMailIcon from '@/icons/full-mail.svg'

import { formatDateTime } from '../../CollectiveOfferSummary/components/utils/formatDatetime'
import styles from '../BookableOfferTimeline.module.scss'

export const BookingWaitingBanner = ({
  offerStatus,
  offerId,
  bookingLimitDatetime,
  departmentCode,
  canEditDates,
  contactEmail,
}: {
  offerStatus:
    | CollectiveOfferDisplayedStatus.PUBLISHED
    | CollectiveOfferDisplayedStatus.PREBOOKED
  offerId: number
  bookingLimitDatetime: string
  departmentCode?: string | null
  canEditDates: boolean
  contactEmail?: string | null
}) => {
  const daysCountBeforeExpiration = differenceInCalendarDays(
    new Date(bookingLimitDatetime),
    new Date()
  )

  const expirationText = getExpirationText(daysCountBeforeExpiration)
  const isExpiringSoon = !!expirationText

  const description =
    offerStatus === CollectiveOfferDisplayedStatus.PUBLISHED
      ? `L'enseignant doit impérativement préréserver l'offre avant le ${formatDateTime(
          bookingLimitDatetime,
          FORMAT_DD_MM_YYYY,
          departmentCode
        )}. Sinon, elle sera automatiquement expirée et vous devrez renseigner une nouvelle date limite de réservation.`
      : `Le chef d'établissement doit impérativement confirmer la préréservation de l'offre avant le ${formatDateTime(
          bookingLimitDatetime,
          FORMAT_DD_MM_YYYY,
          departmentCode
        )}. Sinon, elle sera automatiquement expirée et vous devrez renseigner une nouvelle date limite de réservation.`

  const actions: BannerLink[] = []
  if (canEditDates) {
    actions.push({
      label: 'Modifier la date limite de réservation',
      icon: fullEditIcon,
      href: `/offre/${offerId}/collectif/stocks/edition`,
      type: 'link',
    })
  }
  if (contactEmail && isExpiringSoon) {
    actions.push({
      label: "Contacter l'établissement",
      icon: fullMailIcon,
      href: `mailto:${contactEmail}`,
      isExternal: true,
      type: 'link',
    })
  }

  return (
    <div className={styles['callout']}>
      {isExpiringSoon ? (
        <Banner
          title="Informations"
          variant={BannerVariants.WARNING}
          description={`${expirationText}.\n ${description}`}
          actions={actions}
        />
      ) : (
        <Banner
          title="Informations"
          variant={BannerVariants.DEFAULT}
          description={description}
          actions={actions}
        />
      )}
    </div>
  )
}
