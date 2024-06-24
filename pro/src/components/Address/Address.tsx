import { useField, useFormikContext } from 'formik'
import React, { useState, useEffect } from 'react'

import { apiAdresse } from 'apiClient/adresse/apiAdresse'
import { serializeAdressData } from 'components/Address/serializer'
import { SelectOption } from 'custom_types/form'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { AutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

interface AddressProps {
  description?: string
  suggestionLimit?: number
}

export const AddressSelect = ({
  description,
  suggestionLimit,
}: AddressProps) => {
  const { setFieldValue } = useFormikContext()
  const [options, setOptions] = useState<SelectOption[]>([])
  const [addressesMap, setAddressesMap] = useState<
    Record<string, AutocompleteItemProps>
  >({})
  const [, , { setValue: setSearchValue }] = useField(
    'search-addressAutocomplete'
  )
  const [selectedField, , { setValue: setSelectedValue }] = useField(
    'addressAutocomplete'
  )

  useEffect(() => {
    setOptions([{ label: selectedField.value, value: selectedField.value }])
  }, [selectedField.value])

  const handleSearchFieldChange = async (pattern: string) => {
    await setSearchValue(pattern)
    if (pattern.length >= 3) {
      const response = await getSuggestions(pattern)
      setAddressesMap(
        response.reduce<Record<string, AutocompleteItemProps>>(
          (acc, add: AutocompleteItemProps) => {
            acc[add.label] = add
            return acc
          },
          {}
        )
      )
      setOptions(
        response.map((item) => ({
          value: String(item.value),
          label: item.label,
        }))
      )
    } else if (pattern.length === 0) {
      setOptions([])
      handleAddressSelect(setFieldValue, undefined, { value: pattern })
    }
  }

  const handleSelectedFieldChange = async (value: string) => {
    await setSelectedValue(value)
    handleAddressSelect(setFieldValue, addressesMap[value], { value })
  }

  const getSuggestions = async (search: string) => {
    if (search) {
      try {
        const adressSuggestions = await apiAdresse.getDataFromAddress(
          search,
          suggestionLimit
        )
        return serializeAdressData(adressSuggestions)
      } catch {
        return []
      }
    }
    return []
  }

  return (
    <SelectAutocomplete
      name="addressAutocomplete"
      label="Adresse postale"
      placeholder="Entrez votre adresse et sélectionnez une suggestion"
      options={options}
      hideArrow={true}
      resetOnOpen={false}
      description={description}
      onSearch={handleSearchFieldChange}
      onChange={handleSelectedFieldChange}
    />
  )
}

export const handleAddressSelect = (
  setFieldValue: any,
  selectedItem?: AutocompleteItemProps,
  searchField?: any
) => {
  setFieldValue('street', selectedItem?.extraData.address)
  if (searchField.value) {
    setFieldValue('addressAutocomplete', searchField?.value)
  }
  setFieldValue('postalCode', selectedItem?.extraData.postalCode)
  setFieldValue('city', selectedItem?.extraData.city)
  setFieldValue('latitude', selectedItem?.extraData.latitude)
  setFieldValue('longitude', selectedItem?.extraData.longitude)
  setFieldValue('banId', selectedItem?.value)
}
