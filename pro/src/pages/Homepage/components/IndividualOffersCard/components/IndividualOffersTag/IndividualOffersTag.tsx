import { isAfter } from 'date-fns'

import { type OfferHomeResponseModel, OfferStatus } from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import ticketFullIcon from '@/icons/full-ticket.svg'
import waitFullIcon from '@/icons/full-wait.svg'

type IndividualOffersTagProps = {
  offer: OfferHomeResponseModel
  venueDepartmentCode: string | null
}

export const IndividualOffersTag = ({
  offer,
  venueDepartmentCode,
}: IndividualOffersTagProps): JSX.Element => {
  if (offer.status === OfferStatus.SCHEDULED) {
    const departmentCode = offer.departmentCode ?? venueDepartmentCode ?? ''

    const publicationDate =
      offer.publicationDatetime &&
      isAfter(offer.publicationDatetime, new Date())
        ? formatLocalTimeDateString(
            offer.publicationDatetime,
            departmentCode,
            FORMAT_DD_MM_YYYY_HH_mm
          )
        : null
    if (publicationDate) {
      return (
        <Tag
          label={`Publication : ${publicationDate}`}
          icon={waitFullIcon}
          variant={TagVariant.WARNING}
        />
      )
    }
  }

  return (
    <Tag
      label={`${offer.bookingsCount} ${pluralizeFr(offer.bookingsCount, 'réservation', 'réservations')}`}
      icon={ticketFullIcon}
    />
  )
}
