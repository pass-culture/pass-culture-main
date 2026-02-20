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

type ApiSelectComponent = <T extends ApiOption>(
  props: ApiSelectProps<T> & { ref?: Ref<HTMLInputElement> }
) => JSX.Element | null

export interface ApiOption extends SelectOption {
  [key: string]: unknown
}

export type ApiSelectProps<T extends ApiOption> = {
  name: string
  label: string | JSX.Element
  disabled?: boolean
  className?: string
  description?: string
  error?: string
  required?: boolean
  minSearchLength?: number
  onSelect(option: T | undefined): void
  onSearch?(searchText: string): void
  searchApi: (searchText: string) => Promise<T[]>
  value?: string
  thumbPlaceholder?: string
}

export const ApiSelect = forwardRef(function ApiSelect<T extends ApiOption>(
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
    thumbPlaceholder,
  }: ApiSelectProps<T>,
  ref: Ref<HTMLInputElement>
) {
  const [options, setOptions] = useState<SelectOption[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
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
          data.map(({ value, label, thumbUrl }) => ({
            value,
            label,
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
    onSearch?.(searchText)
  }, DEBOUNCE_TIME_BEFORE_REQUEST)

  // biome-ignore lint/correctness/useExhaustiveDependencies: only run on mount
  useEffect(() => {
    fetchOptions(value ?? inputRef.current?.value ?? '')
  }, [])

  useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

  return (
    <SelectAutocomplete
      name={name}
      label={label}
      options={options}
      thumbPlaceholder={thumbPlaceholder}
      description={description}
      onSearch={(searchText) => {
        debouncedOnSearch(searchText)
      }}
      onChange={(event) => {
        const selectedOption = optionsMap.current.get(event.target.value)
        onSelect(selectedOption)
      }}
      disabled={disabled}
      className={className}
      ref={inputRef}
      error={error}
      required={required}
      value={value}
    />
  )
}) as ApiSelectComponent
