import { type ForwardedRef, useState } from 'react'

import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
import type { CollectiveAdditionalFeeModel } from '@/apiClient/v1'
import {
  type CustomEvent,
  SelectAutocomplete,
} from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import { ADDITIONAL_FEES_OPTIONS } from '../../constants'

type AdditionalFeeTypeInputProps = {
  collectiveAdditionalFee: CollectiveAdditionalFeeModel
  error?: string
  disabled: boolean
  ref: ForwardedRef<HTMLInputElement>
  name: string
  onChange({ type, label }: Omit<CollectiveAdditionalFeeModel, 'amount'>): void
}

function getFeeTypeOrLabel(
  { type, label }: Omit<CollectiveAdditionalFeeModel, 'amount'>,
  previous: string = ''
): string {
  const fallbackLabel = previous === '--' ? '' : '--'
  return type === CollectiveAdditionalFeeType.OTHER
    ? (label ?? fallbackLabel)
    : type
}

export const AdditionalFeeTypeInput = ({
  collectiveAdditionalFee: { type, label },
  error,
  disabled,
  ref,
  name,
  onChange,
}: AdditionalFeeTypeInputProps): JSX.Element => {
  const [creatableOption, setCreatableOption] = useState<string>()

  // const [typeOrLabel, setTypeOrLabel] = useState<string>(() =>
  //   getFeeTypeOrLabel({ type, label })
  // )

  const [currentFee, setCurrentFee] = useState<
    Omit<CollectiveAdditionalFeeModel, 'amount'>
  >({ type, label })

  const typeOrLabel = getFeeTypeOrLabel(currentFee)

  function onInputSelect({
    target: { value: feeSelectedTypeOrLabel },
  }: CustomEvent<'change'>) {
    const selectedOption = ADDITIONAL_FEES_OPTIONS.find(
      (option) => option.value === feeSelectedTypeOrLabel
    )
    let newFee: Omit<CollectiveAdditionalFeeModel, 'amount'>
    if (selectedOption) {
      newFee = { type: selectedOption.value, label: null }
    } else {
      newFee = {
        type: CollectiveAdditionalFeeType.OTHER,
        label: feeSelectedTypeOrLabel,
      }
    }
    onChange(newFee)
    setCurrentFee(newFee)
    // setTypeOrLabel((previous) => getFeeTypeOrLabel(newFee, previous))
  }

  function onSearch(pattern: string) {
    const matchesExistingOption = ADDITIONAL_FEES_OPTIONS.some(
      (option) => option.label === pattern
    )
    setCreatableOption(matchesExistingOption ? undefined : pattern)
  }

  function onBlur({ target: { value } }: CustomEvent<'blur'>) {
    console.log('BLUR', value, typeOrLabel, type, label, {
      type,
      label,
    })
    if (value !== typeOrLabel) {
      // On est dans le cas où le fee n'a pas été selectionné.
      setCurrentFee({
        type,
        label: label ?? (value ? '--' : ''),
      })
    }
  }

  console.log('typeOrLabel', typeOrLabel)

  return (
    <SelectAutocomplete
      label="Type de frais annexes"
      value={typeOrLabel}
      options={ADDITIONAL_FEES_OPTIONS}
      searchInOptions={(options, pattern) =>
        options
          .filter((o) => o.value !== CollectiveAdditionalFeeType.OTHER)
          .filter((o) =>
            o.label.toLowerCase().includes(pattern.trim().toLowerCase())
          )
      }
      required
      disabled={disabled}
      name={name}
      // className={styles['additional-fee-type-select']}
      creatableOption={creatableOption}
      onChange={onInputSelect}
      onSearch={onSearch}
      onBlur={onBlur}
      shouldResetOnOpen
      error={error}
      ref={ref}
    />
  )
}
