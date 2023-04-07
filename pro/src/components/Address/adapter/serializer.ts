import { IAdresseData } from 'apiClient/adresse/types'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

export const serializeAdressData = (
  adressData: IAdresseData[]
): IAutocompleteItemProps[] => {
  return adressData.map(data => ({
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
