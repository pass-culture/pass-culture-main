import { FieldInputProps } from 'formik'

import { AdresseData } from 'apiClient/adresse/types'


export interface AutocompleteItemProps {
  value: string | number
  label: string
  disabled?: boolean
  extraData?: Partial<AdresseData>
}


export const handleAddressSelect = (
  setFieldValue: any,
  selectedItem?: AutocompleteItemProps,
  searchField?: FieldInputProps<string>
) => {
  setFieldValue('street', selectedItem?.extraData?.address ?? '')
  if (searchField) {
    setFieldValue('addressAutocomplete', searchField.value)
  }
  setFieldValue('postalCode', selectedItem?.extraData?.postalCode ?? '')
  setFieldValue('city', selectedItem?.extraData?.city ?? '')
  setFieldValue('latitude', selectedItem?.extraData?.latitude ?? '')
  setFieldValue('longitude', selectedItem?.extraData?.longitude ?? '')
  setFieldValue('banId', selectedItem?.value ?? '')
  setFieldValue('inseeCode', selectedItem?.extraData?.inseeCode ?? '')
}
