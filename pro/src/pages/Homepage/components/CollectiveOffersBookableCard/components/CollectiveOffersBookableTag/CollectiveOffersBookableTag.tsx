import { differenceInCalendarDays } from 'date-fns'

import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1/new'
import { canExpire } from '@/commons/core/OfferEducational/utils/canExpire'
import { getExpirationText } from '@/commons/core/OfferEducational/utils/getExpirationText'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import calendarIcon from '@/icons/full-calendar.svg'
import waitIcon from '@/icons/full-wait.svg'

type CollectiveOffersBookableTagProps = {
  stock: NonNullable<CollectiveOfferHomeResponseModel['collectiveStock']>
  displayedStatus: CollectiveOfferHomeResponseModel['displayedStatus']
}

export function getTagInfo(
  displayedStatus: CollectiveOfferHomeResponseModel['displayedStatus'],
  stock: NonNullable<CollectiveOfferHomeResponseModel['collectiveStock']>
): { label: string; isExpiring: boolean } {
  if (canExpire({ displayedStatus })) {
    const daysBeforeExpiration = differenceInCalendarDays(
      new Date(stock.bookingLimitDatetime),
      new Date()
    )
    const expirationText = getExpirationText(daysBeforeExpiration)
    if (expirationText) {
      return { label: expirationText, isExpiring: true }
    }
  }

  const daysBeforeStart = differenceInCalendarDays(
    new Date(stock.startDatetime),
    new Date()
  )
  const label =
    daysBeforeStart > 0
      ? `Dans ${daysBeforeStart} ${pluralizeFr(daysBeforeStart, 'jour', 'jours')}`
      : "Aujourd'hui"

  return { label, isExpiring: false }
}

export const CollectiveOffersBookableTag = ({
  displayedStatus,
  stock,
}: CollectiveOffersBookableTagProps): JSX.Element => {
  const { label, isExpiring } = getTagInfo(displayedStatus, stock)

  return (
    <Tag
      variant={isExpiring ? TagVariant.WARNING : TagVariant.DEFAULT}
      icon={isExpiring ? waitIcon : calendarIcon}
      label={label}
    />
  )
}
