import { isAfter } from 'date-fns'

import { type ListOffersOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import waitFullIcon from '@/icons/full-wait.svg'

export type OfferBookingCellProps = {
  offer: ListOffersOfferResponseModel
  className?: string
}

export const OfferBookingCell = ({ offer }: OfferBookingCellProps) => {
  const departmentCode = getDepartmentCode(offer)

  const bookableDate =
    [OfferStatus.SCHEDULED, OfferStatus.PUBLISHED].includes(offer.status) &&
    offer.bookingAllowedDatetime &&
    isAfter(offer.bookingAllowedDatetime, new Date())
      ? formatLocalTimeDateString(
          offer.bookingAllowedDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : null

  return (
    <div>
      {bookableDate ? (
        <span style={{ whiteSpace: 'nowrap' }}>
          <Tag
            label={bookableDate}
            icon={waitFullIcon}
            variant={TagVariant.WARNING}
          />
        </span>
      ) : (
        offer.bookingsCount || '-'
      )}
    </div>
  )
}
