import { useField, useFormikContext } from 'formik'
import { useEffect, useState } from 'react'
import { useDebouncedCallback } from 'use-debounce'

import { getDataFromAddress } from 'apiClient/adresse/apiAdresse'
import { AdresseData, FeaturePropertyType } from 'apiClient/adresse/types'
import { SelectOption } from 'commons/custom_types/form'
import { handleAddressSelect } from 'commons/utils/handleAddressSelect'
import { normalizeStrForAdressSearch } from 'commons/utils/searchPatternInOptions'
import { serializeAdressData } from 'components/Address/serializer'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import { DEBOUNCE_TIME_BEFORE_REQUEST } from './constants'

interface AddressProps {
  description?: string
  suggestionLimit?: number
  onlyTypes?: FeaturePropertyType[]
  disabled?: boolean
  className?: string
  onAddressSelect?: () => void
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
  onlyTypes,
  disabled = false,
  className,
  onAddressSelect,
}: AddressProps) => {
  const { setFieldValue } = useFormikContext()
  const [options, setOptions] = useState<SelectOption[]>([])
  const [addressesMap, setAddressesMap] = useState<
    Record<string, AutocompleteItemProps>
  >({})
  const [searchField, searchFieldMeta] = useField('search-addressAutocomplete')
  const [selectedField] = useField('addressAutocomplete')
  useEffect(() => {
    setOptions([{ label: selectedField.value, value: selectedField.value }])
  }, [selectedField.value])

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
    } else if (searchField.value.length === 0 && searchFieldMeta.touched) {
      setOptions([])
      handleAddressSelect(setFieldValue, undefined, searchField)
      onAddressSelect?.()
    }
  }

  const debouncedOnSearch = useDebouncedCallback(
    onSearchFieldChange,
    DEBOUNCE_TIME_BEFORE_REQUEST
  )

  // TODO we should not use useEffect for this but an event handler on the input
  useEffect(() => {
    // False positive, eslint disable can be removed when noUncheckedIndexedAccess is enabled in TS config
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    if (addressesMap[searchField.value] !== undefined) {
      handleAddressSelect(
        setFieldValue,
        addressesMap[searchField.value],
        searchField
      )
      onAddressSelect?.()
    }
  }, [selectedField.value])

  /* istanbul ignore next: DEBT, TO FIX */
  const getSuggestions = async (search: string) => {
    if (search) {
      try {
        const addressSuggestions = await getDataFromAddress(search, {
          limit: suggestionLimit,
          onlyTypes,
        })
        return serializeAdressData(addressSuggestions)
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
      options={options}
      hideArrow={true}
      resetOnOpen={false}
      description={description}
      searchInOptions={searchInOptions}
      onSearch={debouncedOnSearch}
      disabled={disabled}
      className={className}
    />
  )
}
