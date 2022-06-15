import { BaseCheckbox, BaseInput, FieldLayout } from '../shared'
import React, { useEffect, useRef, useState } from 'react'
import { useField, useFormikContext } from 'formik'

import AutocompleteList from '../shared/AutocompleteList/AutocompleteList'
import cx from 'classnames'
import styles from './SelectAutocomplete.module.scss'

export type SelectAutocompleteProps = {
  label: string
  fieldName: string
  smallLabel?: boolean
  isOptional?: boolean
  hideFooter?: boolean
  options: SelectOption[]
  className?: string
  disabled?: boolean
  filterLabel?: string
  onSearchChange?: () => void
}

const SelectAutocomplete = ({
  label,
  fieldName,
  smallLabel = false,
  isOptional = false,
  hideFooter = false,
  options,
  className,
  disabled = false,
  filterLabel,
  onSearchChange,
}: SelectAutocompleteProps): JSX.Element => {
  const { setFieldValue, setFieldTouched } = useFormikContext<any>()
  const [field, meta, helpers] = useField(fieldName)
  const [searchField] = useField(`search-${fieldName}`)

  const containerRef = useRef<HTMLDivElement>(null)

  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    if (containerRef.current) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [containerRef])

  useEffect(() => {
    if (onSearchChange) {
      onSearchChange()
      return
    }
    const regExp = new RegExp(searchField.value, 'i')
    setFilteredOptions(
      options.filter(
        option => searchField.value === '' || option.label.match(regExp)
      )
    )
  }, [searchField.value])

  return (
    <FieldLayout
      label={label}
      name={`search-${fieldName}`}
      error={meta.error}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      isOptional={isOptional}
      hideFooter={hideFooter}
      className={className}
    >
      <div
        className={cx(styles['select-autocomplete-container'], className)}
        ref={containerRef}
      >
        <BaseInput
          onFocus={() => {
            if (!isOpen) {
              setIsOpen(true)
              setFieldValue(`search-${fieldName}`, '', false)
            }
            setFieldTouched(fieldName, true)
          }}
          placeholder={label}
          hasError={meta.touched && !!meta.error}
          type="text"
          disabled={disabled}
          className={styles['select-autocomplete-input']}
          autoComplete="off"
          {...searchField}
        />
        <AutocompleteList
          className={styles['menu']}
          onButtonClick={() => {
            if (isOpen) {
              setIsOpen(false)
            } else {
              setFieldValue(`search-${fieldName}`, '', false)
              setIsOpen(true)
            }
            setFieldTouched(fieldName, true)
          }}
          isOpen={isOpen}
          filteredOptions={[
            ...filteredOptions,
            ...(filterLabel
              ? [{ value: filterLabel, label: filterLabel, disabled: true }]
              : []),
          ]}
          renderOption={({ value, label, disabled }) => (
            <BaseCheckbox
              label={label}
              key={`${fieldName}-${value}`}
              className={styles['option']}
              value={value}
              id={`${fieldName}-${value}`}
              name={fieldName}
              role="option"
              aria-selected={field.value === value}
              disabled={disabled}
              checked={field.value === value}
              onClick={() => {
                helpers.setValue(value)
                setIsOpen(false)
                setFieldValue(`search-${fieldName}`, label, false)
              }}
            />
          )}
        />
      </div>
    </FieldLayout>
  )
}

export default SelectAutocomplete
