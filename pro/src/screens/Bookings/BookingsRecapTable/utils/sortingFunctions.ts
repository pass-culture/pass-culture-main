import { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

export const sortByOfferName = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  firstRow: Row<T>,
  secondRow: Row<T>
) => {
  const offerNameOne = firstRow.original.stock.offer_name
  const offerNameTwo = secondRow.original.stock.offer_name
  return offerNameOne.localeCompare(offerNameTwo, 'fr', { sensitivity: 'base' })
}

export const sortByBeneficiaryName = (
  firstRow: Row<BookingRecapResponseModel>,
  secondRow: Row<BookingRecapResponseModel>
) => {
  let beneficiaryOne = firstRow.original.beneficiary.lastname
  let beneficiaryTwo = secondRow.original.beneficiary.lastname

  const lastNamesAreTheSame = Boolean(
    (beneficiaryOne ?? '').localeCompare(beneficiaryTwo ?? '', 'fr', {
      sensitivity: 'base',
    }) === 0
  )
  if (lastNamesAreTheSame) {
    beneficiaryOne = firstRow.original.beneficiary.firstname
    beneficiaryTwo = secondRow.original.beneficiary.firstname
  }
  return (beneficiaryOne ?? '').localeCompare(beneficiaryTwo ?? '', 'fr', {
    sensitivity: 'base',
  })
}

export const sortByInstitutionName = (
  firstRow: Row<CollectiveBookingResponseModel>,
  secondRow: Row<CollectiveBookingResponseModel>
) => {
  const institutionOne = firstRow.original.institution
  const institutionTwo = secondRow.original.institution
  const institutionOneName =
    `${institutionOne.institutionType} ${institutionOne.name}`.trim()
  const institutionTwoName =
    `${institutionTwo.institutionType} ${institutionTwo.name}`.trim()

  return institutionOneName.localeCompare(institutionTwoName, 'fr', {
    sensitivity: 'base',
  })
}

export const sortByBookingDate = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  firstRow: Row<T>,
  secondRow: Row<T>
) => {
  const bookingDateOne = new Date(firstRow.original.booking_date)
  const bookingDateTwo = new Date(secondRow.original.booking_date)
  if (bookingDateOne > bookingDateTwo) {
    return 1
  } else if (bookingDateOne < bookingDateTwo) {
    return -1
  }
  return 0
}
