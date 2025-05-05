import { forwardRef, Ref, useImperativeHandle, useRef, useState } from 'react'
import { useDebouncedCallback } from 'use-debounce'

import { AdresseData, FeaturePropertyType } from 'apiClient/adresse/types'
import { getDataFromAddress } from 'apiClient/api'
import { SelectOption } from 'commons/custom_types/form'
import { normalizeStrForAdressSearch } from 'commons/utils/searchPatternInOptions'
import {
  DEBOUNCE_TIME_BEFORE_REQUEST,
  DEFAULT_SUGGESTION_LIMIT,
} from 'components/Address/constants'
import { SelectAutocomplete } from 'ui-kit/formV2/SelectAutoComplete/SelectAutocomplete'

type AddressSelectProps = {
  name: string
  label: string | JSX.Element
  onChange(event: React.ChangeEvent<HTMLInputElement>): void
  onBlur(event: React.FocusEvent<HTMLInputElement>): void
  onAddressChosen(data: AdresseData): void
  disabled?: boolean
  className?: string
  description?: string
  onlyTypes?: FeaturePropertyType[]
  error?: string
  suggestionLimit?: number
  isOptional?: boolean
}

export const AddressSelect = forwardRef(
  (
    {
      label,
      description,
      suggestionLimit = DEFAULT_SUGGESTION_LIMIT,
      onlyTypes,
      disabled = false,
      className,
      onAddressChosen = () => {},
      error,
      name,
      onChange = () => {},
      onBlur = () => {},
      isOptional,
    }: AddressSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const [searchField, setSearchField] = useState('') // Represents the value of the searched address
    const [options, setOptions] = useState<SelectOption[]>([]) // Represents the address suggestions (that can change asynchronously)

    const addressesMap = useRef<Map<string, AdresseData>>(new Map())
    const inputRef = useRef<HTMLInputElement>(null) // Ref to pass to <SelectAutoComplete />

    // Handles the "Adresse API" call when searchField change (debounced), and updates the address suggestions
    const onSearchFieldChange = async () => {
      // "Adresse API" search’s minimum is 3 characters
      if (searchField.trim().length < 3) {
        setOptions([])
        return
      }

      // API Call
      try {
        const addressSuggestions = await getDataFromAddress(searchField, {
          limit: suggestionLimit,
          onlyTypes,
        })

        // Updates the map to have the good address data
        addressesMap.current = new Map(
          addressSuggestions.map((address) => [address.label, address])
        )
        setOptions(
          addressSuggestions.map(({ label }) => ({
            value: label,
            label,
          }))
        )
      } catch {
        addressesMap.current = new Map()
        setOptions([])
      }
    }

    const debouncedOnSearch = useDebouncedCallback(
      onSearchFieldChange,
      DEBOUNCE_TIME_BEFORE_REQUEST
    )

    // Better search function that allows to find addresses labels with accents or separate words
    const searchInOptions = (options: SelectOption[], pattern: string) =>
      options.filter((option) =>
        normalizeStrForAdressSearch(pattern || '')
          .split(' ')
          .every((word) =>
            normalizeStrForAdressSearch(option.label).includes(word)
          )
      )

    // Connect the external reference to the internal one "inputRef", allowing to get the input’s initial value if applicable
    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <SelectAutocomplete
        name={name}
        label={label}
        options={options}
        hideArrow={true}
        resetOnOpen={false}
        description={description}
        onSearch={(searchText) => {
          setSearchField(searchText)
          void debouncedOnSearch()
        }}
        onChange={(event) => {
          // @ts-expect-error
          onChange(event)
          const addressData = addressesMap.current.get(event.target.value)
          if (addressData) {
            onAddressChosen(addressData)
          }
        }}
        onBlur={(event) => {
          // If the "value" returned by the component is empty, we synchronize this with empty address fields
          if (event.target.value.trim() === '') {
            onAddressChosen({
              id: '',
              address: '',
              city: '',
              label: '',
              // @ts-expect-error : Little hack because all the fields "latitude/longitude" are treated as strings in forms
              latitude: '',
              // @ts-expect-error : idem
              longitude: '',
              postalCode: '',
              inseeCode: '',
            })
          }
          // @ts-expect-error
          onBlur(event)
        }}
        searchInOptions={searchInOptions}
        disabled={disabled}
        className={className}
        ref={inputRef}
        error={error}
        isOptional={isOptional}
      />
    )
  }
)

AddressSelect.displayName = 'AddressSelect'
