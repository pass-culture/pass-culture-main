import {
  CollectiveOfferOfferVenueResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

export const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

export const getLocalBeginningDatetime = (
  beginningDatetime: string,
  venuePostalCode: string | null | undefined
): string => {
  if (!venuePostalCode) return ''

  const departmentCode = extractDepartmentCode(venuePostalCode)
  const stockBeginningDate = new Date(beginningDatetime)
  const stockBeginningDateISOString =
    toISOStringWithoutMilliseconds(stockBeginningDate)
  const stockLocalBeginningDate = formatLocalTimeDateString(
    stockBeginningDateISOString,
    departmentCode,
    'dd/MM/yyyy à HH:mm'
  )

  return stockLocalBeginningDate
}

export const getOfferVenue = (
  offerVenue: CollectiveOfferOfferVenueResponseModel
): string => {
  if (offerVenue.addressType === OfferAddressType.OTHER) {
    return offerVenue.otherAddress
  }

  if (offerVenue.addressType === OfferAddressType.SCHOOL) {
    return 'Dans l’établissement scolaire'
  }

  return 'Dans votre lieu'
}

export const getStudentsLabel = (students: StudentLevels[]) =>
  students ? (students?.length > 1 ? 'Multi niveaux' : students[0]) : ''
