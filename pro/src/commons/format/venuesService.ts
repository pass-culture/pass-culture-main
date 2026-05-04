import type {
  GetOffererAddressesResponseModel,
  LocationResponseModel,
} from '@/apiClient/v1'

type MinimalAddressResponseModelToDisplay = Pick<
  LocationResponseModel,
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

export const formatAndOrderAddresses = (
  addresses: GetOffererAddressesResponseModel
) =>
  addresses
    .map((offerAddress) => ({
      value: offerAddress.id.toString(),
      label: computeAddressDisplayName(offerAddress),
    }))
    .sort((a, b) =>
      a.label.localeCompare(b.label, 'fr', { sensitivity: 'base' })
    )
