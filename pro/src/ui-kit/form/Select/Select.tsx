import { useField } from 'formik'
import React, { useCallback } from 'react'

import { SelectOption } from 'custom_types/form'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import SelectInput from './SelectInput'

export type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement> &
  FieldLayoutBaseProps & {
    defaultOption?: SelectOption | null
    options: SelectOption[]
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
  isLabelHidden,
  classNameLabel,
  classNameFooter,
  ...selectAttributes
}: SelectProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'select' })

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
      isLabelHidden={isLabelHidden}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
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
