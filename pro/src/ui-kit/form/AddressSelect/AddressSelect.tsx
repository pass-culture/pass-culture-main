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
import type { SelectOption } from '@/commons/custom_types/form'
import { normalizeStrForSearch } from '@/commons/utils/normalizeStrForSearch'
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
    const [addressOptions, setAddressOptions] = useState<SelectOption[]>([])
    const addressesMap = useRef<Map<string, AdresseData>>(new Map())
    const inputRef = useRef<HTMLInputElement>(null) // Ref to pass to <SelectAutoComplete />

    const fetchOptions = useCallback(
      async (searchText: string) => {
        if (searchText.trim().length < 3) {
          setAddressOptions([])
          return
        }

        try {
          const addressSuggestions = await getDataFromAddress(searchText, {
            limit: suggestionLimit,
            onlyTypes,
          })

          addressesMap.current = new Map(
            addressSuggestions.map((address) => [address.label, address])
          )
          setAddressOptions(
            addressSuggestions.map(({ label }) => ({
              value: label,
              label,
            }))
          )
        } catch {
          addressesMap.current = new Map()
          setAddressOptions([])
        }
      },
      [suggestionLimit, onlyTypes]
    )

    const debouncedOnSearch = useDebouncedCallback((searchText: string) => {
      fetchOptions(searchText)
    }, DEBOUNCE_TIME_BEFORE_REQUEST)

    const normalizeStrForAdressSearch = (str: string): string => {
      return normalizeStrForSearch(str).replace(/[^\w ]/, '')
    }

    const searchInOptions = (options: SelectOption[], pattern: string) =>
      options.filter((option) =>
        normalizeStrForAdressSearch(pattern || '')
          .split(' ')
          .every((word) =>
            normalizeStrForAdressSearch(option.label).includes(word)
          )
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
        options={addressOptions}
        description={description}
        onSearch={(searchText) => {
          debouncedOnSearch(searchText)
        }}
        onChange={(event) => {
          onChange?.(event)
          const addressData = addressesMap.current.get(event.target.value)
          if (addressData) {
            onAddressChosen?.(addressData)
          }
        }}
        onBlur={(event) => {
          onBlur?.(event)
          const addressData = addressesMap.current.get(event.target.value)
          if (addressData) {
            onAddressChosen?.(addressData)
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
