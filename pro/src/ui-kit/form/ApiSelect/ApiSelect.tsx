import { useCallback, useEffect, useRef, useState } from 'react'
import { useDebouncedCallback } from 'use-debounce'

import type { ApiOption, SelectOption } from '@/commons/custom_types/form'
import { SelectAutocomplete } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

export type ApiSelectProps<T extends ApiOption> = Readonly<{
  name: string
  label: string | JSX.Element
  disabled?: boolean
  className?: string
  description?: string
  error?: string
  required?: boolean
  minSearchLength?: number
  onSelect(option: T | undefined): void
  onCreate(value: string): void
  onReset(): void
  searchApi: (searchText: string) => Promise<T[]>
  value?: string
  thumbPlaceholder?: string
}>

export function ApiSelect<T extends ApiOption>({
  name,
  label,
  disabled = false,
  className,
  description,
  error,
  required = true,
  minSearchLength = 3,
  onSelect,
  onCreate,
  onReset,
  searchApi,
  value: currentValue,
  thumbPlaceholder,
}: ApiSelectProps<T>) {
  const [options, setOptions] = useState<SelectOption[]>([])
  const [value, setValue] = useState<string>(currentValue ?? '')
  const optionsMap = useRef<Map<string, T>>(new Map())

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
          data.map(({ value, label, description, thumbUrl }) => ({
            value,
            label,
            description,
            thumbUrl,
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
  }, DEBOUNCE_TIME_BEFORE_REQUEST)

  // biome-ignore lint/correctness/useExhaustiveDependencies: only run on mount
  useEffect(() => {
    value && fetchOptions(value)
  }, [])

  const creatableOption = value.length >= minSearchLength ? value : undefined

  return (
    <SelectAutocomplete
      name={name}
      label={label}
      options={options}
      thumbPlaceholder={thumbPlaceholder}
      description={description}
      onSearch={(searchText) => {
        if (searchText === '') {
          onReset()
        }
        setValue(searchText)
        debouncedOnSearch(searchText)
      }}
      onChange={(event) => {
        const selectedOption = optionsMap.current.get(event.target.value)
        if (selectedOption) {
          onSelect(selectedOption)
        } else {
          onCreate(event.target.value)
        }
      }}
      onBlur={() => {
        setValue(currentValue ?? '')
        debouncedOnSearch(currentValue ?? '')
      }}
      creatableOption={creatableOption}
      disabled={disabled}
      className={className}
      error={error}
      required={required}
      value={value}
    />
  )
}
