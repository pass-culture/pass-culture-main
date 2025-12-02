import {
  forwardRef,
  type Ref,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import { useDebouncedCallback } from 'use-debounce'

import type {
  AdresseData,
  FeaturePropertyType,
} from '@/apiClient/adresse/types'
import { getDataFromAddress } from '@/apiClient/api'
import { normalizeStrForAdressSearch } from '@/commons/utils/searchPatternInOptions'
import {
  type CustomEvent,
  SelectAutocomplete,
} from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400
const DEFAULT_SUGGESTION_LIMIT = 5

export type AddressSelectProps = {
  /** Name of the field, used for form submission and accessibility */
  name: string
  /** Label displayed above the input */
  label: string | JSX.Element
  /** Called when the input value changes */
  onChange?(event: CustomEvent<'change'>): void
  /** Called when the input loses focus */
  onBlur?(event: CustomEvent<'blur'>): void
  /** Called when an address is chosen from the suggestions */
  onAddressChosen?(data: AdresseData): void
  /** Disables the input and prevents interaction */
  disabled?: boolean
  /** Additional CSS class names */
  className?: string
  /** Helper text displayed below the input */
  description?: string
  /** Filters the address suggestions by type (e.g., "municipality", "street") */
  onlyTypes?: FeaturePropertyType[]
  /** Error message to display */
  error?: string
  /** Maximum number of address suggestions to display */
  suggestionLimit?: number
  /** Indicates if the field is required */
  required?: boolean
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
      onAddressChosen,
      error,
      name,
      onChange,
      onBlur,
      required = true,
    }: AddressSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const [addressSuggestions, setAddressSuggestions] = useState<AdresseData[]>(
      []
    )
    const inputRef = useRef<HTMLInputElement>(null) // Ref to pass to <SelectAutoComplete />

    const fetchOptions = useCallback(
      async (searchText: string) => {
        if (searchText.trim().length < 3) {
          setAddressSuggestions([])
          return
        }

        try {
          const addressSuggestions = await getDataFromAddress(searchText, {
            limit: suggestionLimit,
            onlyTypes,
          })

          setAddressSuggestions(addressSuggestions)
        } catch {
          setAddressSuggestions([])
        }
      },
      [suggestionLimit, onlyTypes]
    )

    const debouncedOnSearch = useDebouncedCallback((searchText: string) => {
      void fetchOptions(searchText)
    }, DEBOUNCE_TIME_BEFORE_REQUEST)

    const searchInOptions = (options: string[], pattern: string) =>
      options.filter((option) =>
        normalizeStrForAdressSearch(pattern || '')
          .split(' ')
          .every((word) => normalizeStrForAdressSearch(option).includes(word))
      )

    // biome-ignore lint/correctness/useExhaustiveDependencies: only run on mount
    useEffect(() => {
      if (inputRef.current?.value) {
        fetchOptions(inputRef.current?.value)
      }
    }, [])

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <SelectAutocomplete
        name={name}
        label={label}
        options={addressSuggestions?.map(({ label }) => label) ?? []}
        description={description}
        onChange={(event) => {
          void debouncedOnSearch(event.target.value)
          onChange?.(event)
        }}
        onBlur={(event) => {
          const addressData = addressSuggestions.find(
            ({ label }) => label === event.target.value
          )
          if (addressData) {
            onBlur?.(event)
            onAddressChosen?.(addressData)
          } else {
            onBlur?.({
              type: 'blur',
              target: { name, value: '' },
            })
            onAddressChosen?.({
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
        }}
        searchInOptions={searchInOptions}
        disabled={disabled}
        className={className}
        ref={inputRef}
        error={error}
        required={required}
      />
    )
  }
)

AddressSelect.displayName = 'AddressSelect'
