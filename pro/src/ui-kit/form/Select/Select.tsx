import { useField } from 'formik'
import React, { useCallback, useEffect } from 'react'

import { SelectOption } from 'custom_types/form'

import { FieldLayout } from '../shared'

import SelectInput from './SelectInput'

interface ISelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  name: string
  defaultOption?: SelectOption | null
  options: SelectOption[]
  className?: string
  disabled?: boolean
  label: string
  isOptional?: boolean
  smallLabel?: boolean
  hideFooter?: boolean
  description?: string
  inline?: boolean
}

const Select = ({
  name,
  defaultOption = null,
  options,
  className,
  isOptional = false,
  disabled,
  label,
  smallLabel,
  hideFooter,
  description,
  inline,
  onChange,
  ...selectAttributes
}: ISelectProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'select' })

  useEffect(() => {
    if (
      !isOptional &&
      options.length === 1 &&
      field.value !== options[0].value
    ) {
      helpers.setValue(options[0].value)
    }
  }, [options, helpers, field, isOptional])

  const onCustomChange = useCallback(
    async (e: React.ChangeEvent<HTMLSelectElement>) => {
      field.onChange(e)
      if (onChange) {
        onChange(e)
      }
    },
    [field, onChange]
  )

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={hideFooter}
      isOptional={isOptional}
      label={label}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      inline={inline}
    >
      <SelectInput
        disabled={disabled}
        hasError={meta.touched && !!meta.error}
        hasDescription={description !== undefined}
        options={options}
        defaultOption={defaultOption}
        {...field}
        {...selectAttributes}
        onChange={e => onCustomChange(e)}
      />

      {description && <span>{description}</span>}
    </FieldLayout>
  )
}

export default Select
