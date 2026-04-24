import { differenceInCalendarDays } from 'date-fns'

import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1'
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

export const CollectiveOffersBookableTag = ({
  displayedStatus,
  stock,
}: CollectiveOffersBookableTagProps): JSX.Element => {
  if (canExpire({ displayedStatus })) {
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
