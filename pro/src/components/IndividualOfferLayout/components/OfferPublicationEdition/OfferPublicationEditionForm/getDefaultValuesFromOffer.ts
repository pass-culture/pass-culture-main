import { format, isAfter } from 'date-fns'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { FORMAT_HH_mm, formatShortDateForInput } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type { EventPublicationEditionFormValues } from './types'

export function getDefaultValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  publicationHoursOptions: SelectOption[]
) {
  let publicationMode: EventPublicationEditionFormValues['publicationMode'] =
    null
  if (
    offer.publicationDatetime &&
    isAfter(offer.publicationDatetime, new Date())
  ) {
    publicationMode = 'later'
  } else {
    publicationMode = 'now'
  }

  const publicationTime = offer.publicationDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(offer.publicationDatetime),
        FORMAT_HH_mm
      )
    : undefined

  return {
    publicationMode,
    publicationDate: offer.publicationDatetime
      ? formatShortDateForInput(
          getLocalDepartementDateTimeFromUtc(offer.publicationDatetime)
        )
      : undefined,
    //  If the publication date was set by the backend to a date outside of allowed times, reset the field
    publicationTime:
      publicationTime &&
      publicationHoursOptions.map((op) => op.value).includes(publicationTime)
        ? publicationTime
        : undefined,
    bookingAllowedMode:
      offer.bookingAllowedDatetime &&
      isAfter(offer.bookingAllowedDatetime, new Date())
        ? 'later'
        : 'now',
    bookingAllowedDate: offer.bookingAllowedDatetime
      ? formatShortDateForInput(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime)
        )
      : undefined,
    bookingAllowedTime: offer.bookingAllowedDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime),
          FORMAT_HH_mm
        )
      : undefined,
    isPaused: offer.publicationDatetime === null,
  } satisfies EventPublicationEditionFormValues
}
