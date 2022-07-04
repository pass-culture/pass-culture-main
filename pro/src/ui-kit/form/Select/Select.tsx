import React, { useEffect } from 'react'

import { FieldLayout } from '../shared'
import SelectInput from './SelectInput'
import { SelectOption } from 'custom_types/form'
import { useField } from 'formik'

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
    >
      <SelectInput
        disabled={disabled}
        hasError={meta.touched && !!meta.error}
        hasDescription={description !== undefined}
        options={options}
        defaultOption={defaultOption}
        {...selectAttributes}
        {...field}
      />

      {description && <span>{description}</span>}
    </FieldLayout>
  )
}

export default Select
