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
  venueDepartement: string | null
}

function getReservationText(bookingsCount: number): string {
  return `${bookingsCount} ${pluralizeFr(bookingsCount, 'réservation', 'réservations')}`
}

export const IndividualOffersTag = ({
  offer,
  venueDepartement,
}: IndividualOffersTagProps): JSX.Element => {
  if (offer.status === OfferStatus.SCHEDULED) {
    const departmentCode = offer.departmentCode ?? venueDepartement ?? ''

    const publicationDate =
      offer.publicationDatetime &&
      isAfter(offer.publicationDatetime, new Date())
        ? formatLocalTimeDateString(
            offer.publicationDatetime,
            departmentCode,
            FORMAT_DD_MM_YYYY_HH_mm
          )
        : null
    return (
      <Tag
        label={`Publication : ${publicationDate}`}
        icon={waitFullIcon}
        variant={TagVariant.WARNING}
      />
    )
  }

  return (
    <Tag
      label={getReservationText(offer.bookingsCount)}
      icon={ticketFullIcon}
    />
  )
}
