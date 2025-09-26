import type {
  AddressResponseIsLinkedToVenueModel,
  GetOffererAddressesResponseModel,
  GetOffererVenueResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'

type MinimalAddressResponseModelToDisplay = Pick<
  AddressResponseIsLinkedToVenueModel,
  'label' | 'city' | 'street' | 'postalCode'
>
export const computeAddressDisplayName = (
  address: MinimalAddressResponseModelToDisplay,
  showLabel = true
): string => {
  return (
    (showLabel && address.label ? `${address.label} - ` : '') +
    (address.street ? `${address.street} ` : '') +
    `${address.postalCode} ${address.city}`
  )
}

const sortAlphabeticallyByLabel = (a: SelectOption, b: SelectOption) => {
  const aLabel = a.label.toLowerCase()
  const bLabel = b.label.toLowerCase()

  return aLabel < bLabel ? -1 : aLabel > bLabel ? 1 : 0
}

export const formatAndOrderVenues = (
  venues: (VenueListItemResponseModel | GetOffererVenueResponseModel)[]
) =>
  venues
    .map((venue) => ({
      value: venue.id.toString(),
      label: venue.publicName || venue.name,
    }))
    .sort(sortAlphabeticallyByLabel)

export const formatAndOrderAddresses = (
  addresses: GetOffererAddressesResponseModel
) =>
  addresses
    .map((offerAddress) => ({
      value: offerAddress.id.toString(),
      label: computeAddressDisplayName(offerAddress),
    }))
    .sort(sortAlphabeticallyByLabel)
