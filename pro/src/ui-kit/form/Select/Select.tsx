import { useField } from 'formik'
import React, { useCallback } from 'react'

import { SelectOption } from 'commons/custom_types/form'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import { SelectInput, SelectInputVariant } from './SelectInput'

type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement> &
  FieldLayoutBaseProps & {
    defaultOption?: SelectOption | null
    options: SelectOption[]
  }

export const Select = ({
  name,
  defaultOption = null,
  options,
  className,
  isOptional = false,
  disabled,
  label,
  description,
  inline,
  onChange,
  isLabelHidden,
  classNameLabel,
  classNameFooter,
  hideAsterisk,
  ...selectAttributes
}: SelectProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'select' })

  const onCustomChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
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
      isOptional={isOptional}
      label={label}
      name={name}
      showError={meta.touched && !!meta.error}
      inline={inline}
      isLabelHidden={isLabelHidden}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      hideAsterisk={hideAsterisk}
    >
      <SelectInput
        disabled={disabled}
        hasError={meta.touched && !!meta.error}
        hasDescription={description !== undefined}
        options={options}
        defaultOption={defaultOption}
        aria-required={!isOptional}
        {...field}
        {...selectAttributes}
        onChange={(e) => onCustomChange(e)}
        variant={SelectInputVariant.FORM}
      />

      {description && <span>{description}</span>}
    </FieldLayout>
  )
}
