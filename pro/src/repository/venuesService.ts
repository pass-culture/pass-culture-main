import {
  type AddressResponseIsNotLinkToVenueModel,
  GetOffererAddressesResponseModel,
  ListOffersVenueResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'

export const computeVenueDisplayName = (
  venue: VenueListItemResponseModel | ListOffersVenueResponseModel
): string => {
  if (venue.isVirtual) {
    return `${venue.offererName} - Offre numérique`
  } else {
    return venue.publicName || venue.name
  }
}

type MinimalAddressResponseModelToDisplay = Pick<
  AddressResponseIsNotLinkToVenueModel,
  'label' | 'city' | 'street' | 'postalCode'
>
export const computeAddressDisplayName = (
  address: MinimalAddressResponseModelToDisplay,
  showLabel = true
): string => {
  return (
    (showLabel && address.label ? `${address.label} - ` : '') +
    `${address.street} ${address.postalCode} ${address.city}`
  )
}

const sortAlphabeticallyByLabel = (a: SelectOption, b: SelectOption) => {
  const aLabel = a.label.toLowerCase()
  const bLabel = b.label.toLowerCase()

  return aLabel < bLabel ? -1 : aLabel > bLabel ? 1 : 0
}

export const formatAndOrderVenues = (venues: VenueListItemResponseModel[]) =>
  venues
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
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
