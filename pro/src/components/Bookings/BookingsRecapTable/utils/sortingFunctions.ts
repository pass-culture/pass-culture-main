import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient//v1'

export const sortByOfferName = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
  bookingA: T,
  bookingB: T
) => {
  const offerNameOne = bookingA.stock.offerName
  const offerNameTwo = bookingB.stock.offerName
  return offerNameOne.localeCompare(offerNameTwo, 'fr', { sensitivity: 'base' })
}

export const sortByBeneficiaryName = (
  bookingA: BookingRecapResponseModel,
  bookingB: BookingRecapResponseModel
) => {
  let beneficiaryOne = bookingA.beneficiary.lastname
  let beneficiaryTwo = bookingB.beneficiary.lastname

  const lastNamesAreTheSame = Boolean(
    (beneficiaryOne ?? '').localeCompare(beneficiaryTwo ?? '', 'fr', {
      sensitivity: 'base',
    }) === 0
  )
  if (lastNamesAreTheSame) {
    beneficiaryOne = bookingA.beneficiary.firstname
    beneficiaryTwo = bookingB.beneficiary.firstname
  }
  return (beneficiaryOne ?? '').localeCompare(beneficiaryTwo ?? '', 'fr', {
    sensitivity: 'base',
  })
}

export const sortByInstitutionName = (
  bookingA: CollectiveBookingResponseModel,
  bookingB: CollectiveBookingResponseModel
) => {
  const institutionOne = bookingA.institution
  const institutionTwo = bookingB.institution
  const institutionOneName =
    `${institutionOne.institutionType} ${institutionOne.name}`.trim()
  const institutionTwoName =
    `${institutionTwo.institutionType} ${institutionTwo.name}`.trim()

  return institutionOneName.localeCompare(institutionTwoName, 'fr', {
    sensitivity: 'base',
  })
}

export const sortByBookingDate = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>(
  bookingA: T,
  bookingB: T
) => {
  const bookingDateOne = new Date(bookingA.bookingDate)
  const bookingDateTwo = new Date(bookingB.bookingDate)
  if (bookingDateOne > bookingDateTwo) {
    return 1
  } else if (bookingDateOne < bookingDateTwo) {
    return -1
  }
  return 0
}
