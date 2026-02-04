import {
  forwardRef,
  type Ref,
  useCallback,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import { useDebouncedCallback } from 'use-debounce'

import type { SelectOption } from '@/commons/custom_types/form'
import {
  type CustomEvent,
  SelectAutocomplete,
} from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

export interface ApiOption extends SelectOption {
  [key: string]: unknown
}

export type ApiSelectProps = {
  name: string
  label: string | JSX.Element
  disabled?: boolean
  className?: string
  description?: string
  error?: string
  required?: boolean
  minSearchLength?: number

  // ✅ RHF-compatible handlers
  onChange?(event: CustomEvent<'change'>): void
  onBlur?(event: CustomEvent<'blur'>): void

  // ✅ selection callback
  onSelect(option: ApiOption | undefined): void

  // optional
  onSearch?(searchText: string): void
  searchApi: (searchText: string) => Promise<ApiOption[]>
  value?: string
}

export const ApiSelect = forwardRef(
  (
    {
      name,
      label,
      disabled = false,
      className,
      description,
      error,
      required = true,
      minSearchLength = 3,
      onSelect,
      onSearch,
      searchApi,
      value,
      onChange,
      onBlur,
    }: ApiSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const [options, setOptions] = useState<SelectOption[]>([])
    const inputRef = useRef<HTMLInputElement>(null)
    const optionsMap = useRef<Map<string, ApiOption>>(new Map())

    const fetchOptions = useCallback(
      async (searchText: string) => {
        if (searchText.trim().length < minSearchLength) {
          setOptions([])
          return
        }

        try {
          const data = await searchApi(searchText)
          optionsMap.current = new Map(data.map((opt) => [opt.value, opt]))

          setOptions(
            data.map(({ value, label }) => ({
              value,
              label,
            }))
          )
        } catch {
          optionsMap.current = new Map()
          setOptions([])
        }
      },
      [minSearchLength, searchApi]
    )

    const debouncedOnSearch = useDebouncedCallback((searchText: string) => {
      fetchOptions(searchText)
      onSearch?.(searchText)
    }, DEBOUNCE_TIME_BEFORE_REQUEST)

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    const triggerSelectFromValue = (rawValue: string) => {
      const selectedOption = optionsMap.current.get(rawValue)
      onSelect(selectedOption)
    }

    return (
      <SelectAutocomplete
        name={name}
        label={label}
        options={options}
        description={description}
        onSearch={(searchText) => debouncedOnSearch(searchText)}
        onChange={(event) => {
          onChange?.(event) // ✅ let RHF update field value
          triggerSelectFromValue(event.target.value)
        }}
        onBlur={(event) => {
          onBlur?.(event) // ✅ let RHF mark touched / run validation
          // keep old AddressSelect behavior: choose on blur if value matches an option
          triggerSelectFromValue(event.target.value)
        }}
        disabled={disabled}
        className={className}
        ref={inputRef}
        error={error}
        required={required}
        value={value}
      />
    )
  }
)

ApiSelect.displayName = 'ApiSelect'
