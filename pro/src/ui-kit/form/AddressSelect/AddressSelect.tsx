import { forwardRef, type Ref } from 'react'

import type {
  AdresseData,
  FeaturePropertyType,
} from '@/apiClient/adresse/types'
import { getDataFromAddress } from '@/apiClient/api'
import type { CustomEvent } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import { type ApiOption, ApiSelect } from '../ApiSelect/ApiSelect'

const DEFAULT_SUGGESTION_LIMIT = 5

export type AddressSelectProps = {
  name: string
  label: string | JSX.Element
  onChange?(event: CustomEvent<'change'>): void
  onBlur?(event: CustomEvent<'blur'>): void
  onAddressChosen?(data: AdresseData): void
  disabled?: boolean
  className?: string
  description?: string
  onlyTypes?: FeaturePropertyType[]
  error?: string
  suggestionLimit?: number
  required?: boolean
  value?: string
}

type AddressApiOption = ApiOption & { addressData: AdresseData }

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
      value,
    }: AddressSelectProps,
    ref: Ref<HTMLInputElement>
  ) => {
    const searchApi = async (
      searchText: string
    ): Promise<AddressApiOption[]> => {
      const suggestions = await getDataFromAddress(searchText, {
        limit: suggestionLimit,
        onlyTypes,
      })

      return suggestions.map((address) => ({
        value: address.label, // must match input value
        label: address.label,
        addressData: address,
      }))
    }

    return (
      <ApiSelect
        ref={ref}
        name={name}
        label={label}
        description={description}
        disabled={disabled}
        className={className}
        error={error}
        required={required}
        minSearchLength={3}
        value={value}
        searchApi={searchApi}
        onChange={onChange} // ✅ from RHF register
        onBlur={onBlur} // ✅ from RHF register
        onSelect={(option) => {
          const addr = (option as AddressApiOption | undefined)?.addressData
          if (addr) {
            onAddressChosen?.(addr)
          }
        }}
      />
    )
  }
)

AddressSelect.displayName = 'AddressSelect'
