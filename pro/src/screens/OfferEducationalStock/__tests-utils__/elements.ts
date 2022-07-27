import { screen } from '@testing-library/react'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  DETAILS_PRICE_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

export const elements = {
  queryClassicOfferRadio: (): HTMLInputElement | null =>
    screen.queryByLabelText(
      'Je connais la date et le prix de mon offre'
    ) as HTMLInputElement | null,

  queryShowcaseOfferRadio: (): HTMLInputElement | null =>
    screen.queryByLabelText(
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
    ) as HTMLInputElement | null,

  queryPriceDetailsTextarea: (): HTMLTextAreaElement | null =>
    screen.queryByLabelText(DETAILS_PRICE_LABEL, {
      exact: false,
    }) as HTMLTextAreaElement | null,

  queryBeginningDateInput: (): HTMLInputElement | null =>
    screen.queryByLabelText(EVENT_DATE_LABEL) as HTMLInputElement | null,

  queryBeginningTimeInput: (): HTMLInputElement | null =>
    screen.queryByLabelText(EVENT_TIME_LABEL) as HTMLInputElement | null,

  queryNumberOfPlacesInput: (): HTMLInputElement | null =>
    screen.queryByLabelText(NUMBER_OF_PLACES_LABEL) as HTMLInputElement | null,

  queryPriceInput: (): HTMLInputElement | null =>
    screen.queryByLabelText(TOTAL_PRICE_LABEL) as HTMLInputElement | null,

  queryBookingLimitDatetimeInput: (): HTMLInputElement | null =>
    screen.queryByLabelText(
      BOOKING_LIMIT_DATETIME_LABEL
    ) as HTMLInputElement | null,
}
