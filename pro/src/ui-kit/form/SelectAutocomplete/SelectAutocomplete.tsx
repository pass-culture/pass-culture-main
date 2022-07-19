import { BaseCheckbox, BaseInput, FieldLayout } from '../shared'
import React, { useEffect, useRef, useState } from 'react'
import { useField, useFormikContext } from 'formik'

import AutocompleteList from '../shared/AutocompleteList/AutocompleteList'
import cx from 'classnames'
import styles from './SelectAutocomplete.module.scss'
import { toLowerCaseWithoutAccents } from './utils/toLowerCaseWithoutAccents'

export type SelectAutocompleteProps = {
  className?: string
  disabled?: boolean
  fieldName: string
  filterLabel?: string
  hideFooter?: boolean
  isOptional?: boolean
  label: string
  maxDisplayOptions?: number
  maxDisplayOptionsLabel?: string
  maxHeight?: number
  onSearchChange?: () => void
  options: SelectOption[]
  smallLabel?: boolean
  placeholder?: string
  hideArrow?: boolean
}

const SelectAutocomplete = ({
  className,
  disabled = false,
  fieldName,
  hideFooter = false,
  isOptional = false,
  label,
  maxDisplayOptions,
  maxHeight,
  onSearchChange,
  options,
  smallLabel = false,
  placeholder,
  hideArrow = false,
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

    const formattedValue: string = toLowerCaseWithoutAccents(searchField.value)

    const formattedValues = formattedValue.split(' ')

    setFilteredOptions(
      options.filter(option => {
        const formattedLabel = toLowerCaseWithoutAccents(option.label)

        return (
          formattedValues.length === 0 ||
          formattedValues.every(word => formattedLabel.includes(word))
        )
      })
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
          placeholder={placeholder ?? label}
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
          maxHeight={maxHeight}
          isOpen={isOpen}
          filteredOptions={[
            ...filteredOptions.slice(
              0,
              maxDisplayOptions ?? filteredOptions.length
            ),
            ...(maxDisplayOptions && maxDisplayOptions < filteredOptions.length
              ? [
                  {
                    value: '',
                    label: `${maxDisplayOptions} résultats maximum. Veuillez affiner votre recherche`,
                    disabled: true,
                  },
                ]
              : []),
          ]}
          renderOption={({ value, label, disabled }) => (
            <BaseCheckbox
              label={label}
              key={`${fieldName}-${value}`}
              className={cx(styles['option'], {
                [styles['option-disabled']]: disabled,
              })}
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
          hideArrow={hideArrow}
        />
      </div>
    </FieldLayout>
  )
}

export default SelectAutocomplete
