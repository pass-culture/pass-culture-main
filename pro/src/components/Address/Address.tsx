import { FieldInputProps, useField, useFormikContext } from 'formik'
import { useEffect, useState } from 'react'
import { useDebouncedCallback } from 'use-debounce'

import { apiAdresse } from 'apiClient/adresse/apiAdresse'
import { AdresseData } from 'apiClient/adresse/types'
import { serializeAdressData } from 'components/Address/serializer'
import { SelectOption } from 'custom_types/form'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { normalizeStrForAdressSearch } from 'utils/searchPatternInOptions'

import { DEBOUNCE_TIME_BEFORE_REQUEST } from './constants'

interface AddressProps {
  description?: string
  suggestionLimit?: number
}

export interface AutocompleteItemProps {
  value: string | number
  label: string
  disabled?: boolean
  extraData?: Partial<AdresseData>
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
  const [searchField] = useField('search-addressAutocomplete')
  const [selectedField] = useField('addressAutocomplete')
  useEffect(() => {
    setOptions([{ label: selectedField.value, value: selectedField.value }])
  }, [])

  const onSearchFieldChange = async () => {
    if (searchField.value.length >= 3) {
      const response = await getSuggestions(searchField.value)
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
    } else if (searchField.value.length === 0) {
      setOptions([])
      handleAddressSelect(setFieldValue, undefined, searchField)
    }
  }

  const debouncedOnSearch = useDebouncedCallback(
    onSearchFieldChange,
    DEBOUNCE_TIME_BEFORE_REQUEST
  )

  // TODO we should not use useEffect for this but an event handler on the input
  useEffect(() => {
    if (addressesMap[searchField.value] !== undefined) {
      handleAddressSelect(
        setFieldValue,
        addressesMap[searchField.value],
        searchField
      )
    }
  }, [selectedField.value])

  /* istanbul ignore next: DEBT, TO FIX */
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

  function searchInOptions(options: SelectOption[], pattern: string) {
    return options.filter((option) => {
      return normalizeStrForAdressSearch(pattern || '')
        .split(' ')
        .every((word) =>
          normalizeStrForAdressSearch(option.label).includes(word)
        )
    })
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
      searchInOptions={searchInOptions}
      onSearch={debouncedOnSearch}
    />
  )
}

export const handleAddressSelect = (
  setFieldValue: any,
  selectedItem?: AutocompleteItemProps,
  searchField?: FieldInputProps<string>
) => {
  setFieldValue('street', selectedItem?.extraData?.address)
  if (searchField) {
    setFieldValue('addressAutocomplete', searchField.value)
  }
  setFieldValue('postalCode', selectedItem?.extraData?.postalCode)
  setFieldValue('city', selectedItem?.extraData?.city)
  setFieldValue('latitude', selectedItem?.extraData?.latitude)
  setFieldValue('longitude', selectedItem?.extraData?.longitude)
  setFieldValue('banId', selectedItem?.value)
}
