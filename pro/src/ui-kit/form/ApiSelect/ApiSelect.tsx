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

import type { SelectOption } from '@/commons/custom_types/form'
import { SelectAutocomplete } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

export interface ApiOption extends SelectOption {
  [key: string]: unknown
}

export type ApiSelectProps = {
  name: string
  label: string | JSX.Element
  onOptionChosen(option: ApiOption | undefined): void
  getDataFromSearchText: (searchText: string) => Promise<ApiOption[]>
  onOptionSearched?(searchText: string): void
  disabled?: boolean
  className?: string
  description?: string
  error?: string
  required?: boolean
  minSearchLength?: number
}

export const ApiSelect = forwardRef(
  (
    {
      label,
      description,
      disabled = false,
      className,
      onOptionChosen,
      onOptionSearched,
      error,
      name,
      minSearchLength = 3,
      required = true,
      getDataFromSearchText,
    }: ApiSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const [options, setOptions] = useState<SelectOption[]>([])
    const optionsMap = useRef<Map<string, ApiOption>>(new Map())
    const inputRef = useRef<HTMLInputElement>(null)

    const fetchOptions = useCallback(
      async (searchText: string) => {
        if (searchText.trim().length < minSearchLength) {
          setOptions([])
          return
        }

        try {
          const data = await getDataFromSearchText(searchText)
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
      [minSearchLength, getDataFromSearchText]
    )

    const debouncedOnSearch = useDebouncedCallback((searchText: string) => {
      fetchOptions(searchText)
      onOptionSearched?.(searchText)
    }, DEBOUNCE_TIME_BEFORE_REQUEST)

    // biome-ignore lint/correctness/useExhaustiveDependencies: only run on mount
    useEffect(() => {
      fetchOptions(inputRef.current?.value ?? '')
    }, [])

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <SelectAutocomplete
        name={name}
        label={label}
        options={options}
        description={description}
        onSearch={(searchText) => {
          debouncedOnSearch(searchText)
        }}
        onChange={(event) => {
          const selectedOption = optionsMap.current.get(event.target.value)
          onOptionChosen(selectedOption)
        }}
        disabled={disabled}
        className={className}
        ref={inputRef}
        error={error}
        required={required}
      />
    )
  }
)

ApiSelect.displayName = 'ApiSelect'
