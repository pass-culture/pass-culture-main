import { AdresseData } from 'apiClient/adresse/types'

import { AutocompleteItemProps } from './Address'

export const serializeAdressData = (
  adressData: AdresseData[]
): AutocompleteItemProps[] => {
  return adressData.map((data) => ({
    value: data.id,
    label: data.label,
    disabled: false,
    extraData: {
      postalCode: data.postalCode,
      latitude: data.latitude,
      longitude: data.longitude,
      address: data.address,
      city: data.city,
    },
  }))
}
