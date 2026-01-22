import {
  forwardRef,
  type Ref,
  useCallback,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import type { ChangeHandler } from 'react-hook-form'
import { useDebouncedCallback } from 'use-debounce'

import { api } from '@/apiClient/api'
import type { SelectOption } from '@/commons/custom_types/form'
import { SelectAutocomplete } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

type ArtistSelectProps = {
  name: string
  label: string | JSX.Element
  onChange?: ChangeHandler
  disabled?: boolean
  className?: string
  description?: string
  error?: string
  required?: boolean
  value?: string
}

export const ArtistSelect = forwardRef(
  (
    {
      label,
      description,
      disabled = false,
      className,
      error,
      name,
      onChange,
      required = false,
      value,
    }: ArtistSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const [artistOptions, setArtistOptions] = useState<SelectOption[]>([])
    const inputRef = useRef<HTMLInputElement>(null)

    const fetchArtists = useCallback(async (searchText: string) => {
      if (searchText.trim().length < 2) {
        setArtistOptions([])
        return
      }

      try {
        const artists = await api.getArtists(searchText)

        setArtistOptions(
          artists.map((artist: { id: string; name: string }) => ({
            value: artist.id,
            label: artist.name,
          }))
        )
      } catch {
        setArtistOptions([])
      }
    }, [])

    const debouncedOnSearch = useDebouncedCallback((searchText: string) => {
      fetchArtists(searchText)
    }, DEBOUNCE_TIME_BEFORE_REQUEST)

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <SelectAutocomplete
        name={name}
        label={label}
        options={artistOptions}
        description={description}
        onSearch={(searchText) => {
          debouncedOnSearch(searchText)
          onChange?.({
            target: {
              name,
              value: { artistId: '', name: searchText },
            },
            type: 'change',
          })
        }}
        onChange={(e) => {
          const selectedArtist = artistOptions.find(
            (option) => option.value === e.target.value
          )
          onChange?.({
            target: {
              name,
              value: { artistId: e.target.value, name: selectedArtist?.label },
            },
            type: 'change',
          })
        }}
        disabled={disabled}
        className={className}
        error={error}
        required={required}
        value={value}
      />
    )
  }
)

ArtistSelect.displayName = 'ArtistSelect'
