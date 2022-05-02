import React, { useEffect } from 'react'

import { FieldLayout } from '../shared'
import SelectInput from './SelectInput'
import { useField } from 'formik'

type Option = {
  value: string
  label: string
}

interface ISelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  name: string
  defaultOption?: Option | null
  options: Option[]
  className?: string
  disabled?: boolean
  label: string
  isOptional?: boolean
  smallLabel?: boolean
  hideFooter?: boolean
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
        options={options}
        defaultOption={defaultOption}
        {...selectAttributes}
        {...field}
      />
    </FieldLayout>
  )
}

export default Select
