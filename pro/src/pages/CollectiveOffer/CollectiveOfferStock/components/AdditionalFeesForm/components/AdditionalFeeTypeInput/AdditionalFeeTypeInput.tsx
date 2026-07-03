import { type Ref, useState } from 'react'

import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
import type { CollectiveAdditionalFeeModel } from '@/apiClient/v1'
import {
  type CustomEvent,
  SelectAutocomplete,
} from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import { ADDITIONAL_FEES_OPTIONS } from '../../constants'

type AdditionalFeeTypeInputProps = {
  collectiveAdditionalFee: CollectiveAdditionalFeeModel
  className?: string
  error?: string
  disabled: boolean
  ref?: Ref<HTMLInputElement>
  name: string
  onChange({ type, label }: Omit<CollectiveAdditionalFeeModel, 'amount'>): void
}

export const AdditionalFeeTypeInput = ({
  collectiveAdditionalFee: { type, label },
  className,
  error,
  disabled,
  ref,
  name,
  onChange,
}: AdditionalFeeTypeInputProps): JSX.Element => {
  const [creatableOption, setCreatableOption] = useState<string>()
  const [resetKey, setResetKey] = useState(0)

  const [currentFee, setCurrentFee] = useState<
    Omit<CollectiveAdditionalFeeModel, 'amount'>
  >({ type, label })

  function handleChange({ target: { value } }: CustomEvent<'change'>) {
    const selectedOption = ADDITIONAL_FEES_OPTIONS.find(
      (option) => option.value === value
    )
    if (selectedOption) {
      const newFee = {
        type: selectedOption.value as CollectiveAdditionalFeeType,
        label: null,
      }
      setCurrentFee(newFee)
      setCreatableOption(undefined)
      if (selectedOption.value === CollectiveAdditionalFeeType.OTHER) {
        setResetKey((k) => k + 1)
      }
      onChange(newFee)
    } else {
      const newFee = { type: CollectiveAdditionalFeeType.OTHER, label: value }
      setCurrentFee(newFee)
      setCreatableOption(undefined)
      onChange(newFee)
    }
  }

  function onBlur(_e: CustomEvent<'blur'>) {
    if (creatableOption !== undefined) {
      const resetValue = { type, label }
      setCurrentFee(resetValue)
      setCreatableOption(undefined)
      setResetKey((k) => k + 1)
      onChange(resetValue)
    }
  }

  return (
    <SelectAutocomplete
      key={resetKey}
      label="Type de frais annexes"
      value={
        currentFee.type === CollectiveAdditionalFeeType.OTHER
          ? (currentFee.label ?? '')
          : currentFee.type
      }
      options={ADDITIONAL_FEES_OPTIONS.filter(
        (o) => o.value !== CollectiveAdditionalFeeType.OTHER
      )}
      required
      ref={ref}
      name={name}
      className={className}
      error={error}
      disabled={disabled}
      creatableOption={creatableOption}
      onChange={handleChange}
      onBlur={onBlur}
      onSearch={setCreatableOption}
    />
  )
}
