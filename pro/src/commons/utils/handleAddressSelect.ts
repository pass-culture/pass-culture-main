import { FieldInputProps } from 'formik'

import { AutocompleteItemProps } from 'components/Address/Address'

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
}
