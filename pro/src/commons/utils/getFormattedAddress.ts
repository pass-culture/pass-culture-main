import { GetVenueResponseModel } from '@/apiClient//v1'

export const getFormattedAddress = (
  address: GetVenueResponseModel['address']
): string => {
  const street = address?.street ? `${address.street}, ` : ''
  const postalCode = address?.postalCode ? `${address.postalCode} ` : ''
  const city = address?.city ? address.city : ''

  return `${street}${postalCode}${city}`
}
