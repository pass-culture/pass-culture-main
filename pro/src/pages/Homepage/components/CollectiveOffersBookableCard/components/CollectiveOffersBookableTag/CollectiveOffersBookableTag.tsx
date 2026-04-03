import { differenceInCalendarDays } from 'date-fns'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { getExpirationText } from '@/commons/core/OfferEducational/utils/getExpirationText'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import calendarIcon from '@/icons/full-calendar.svg'
import waitIcon from '@/icons/full-wait.svg'

import type { CollectiveOffersVariantMap } from '../../../types'

type CollectiveOffersBookableTagProps = {
  stock: NonNullable<CollectiveOffersVariantMap['BOOKABLE']['collectiveStock']>
  displayedStatus: CollectiveOffersVariantMap['BOOKABLE']['displayedStatus']
}

export const CollectiveOffersBookableTag = ({
  displayedStatus,
  stock,
}: CollectiveOffersBookableTagProps): JSX.Element => {
  const canExpire =
    displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED ||
    displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED

  if (canExpire) {
    const daysCountBeforeExpiration = differenceInCalendarDays(
      new Date(stock.bookingLimitDatetime),
      new Date()
    )
    const expirationText = getExpirationText(daysCountBeforeExpiration)

    if (expirationText) {
      return (
        <Tag
          variant={TagVariant.WARNING}
          icon={waitIcon}
          label={expirationText}
        />
      )
    }
  }

  const daysCountBeforeStart = differenceInCalendarDays(
    new Date(stock.startDatetime),
    new Date()
  )

  const tagLabel =
    daysCountBeforeStart > 0
      ? `Dans ${daysCountBeforeStart} ${pluralizeFr(daysCountBeforeStart, 'jour', 'jours')}`
      : "Aujourd'hui"

  return (
    <Tag variant={TagVariant.DEFAULT} icon={calendarIcon} label={tagLabel} />
  )
}
