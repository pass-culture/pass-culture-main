import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useField, useFormikContext } from 'formik'

import AutocompleteList from '../shared/AutocompleteList'
import BaseCheckbox from '../shared/BaseCheckbox'
import { BaseInput } from '../shared'
import FieldLayout from '../shared/FieldLayout'
import { SelectOption } from 'custom_types/form'
import Tag from 'ui-kit/Tag'
import cx from 'classnames'
import styles from './MultiSelectAutocomplete.module.scss'

export interface MultiSelectAutocompleteProps {
  options: SelectOption[]
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  label: string
  className?: string
  fieldName: string
  pluralLabel: string
  hideFooter?: boolean
  isOptional?: boolean
  smallLabel?: boolean
  hideTags?: boolean
}

const MultiSelectAutocomplete = ({
  options,
  onChange,
  label,
  fieldName,
  className,
  pluralLabel,
  hideFooter = false,
  isOptional = false,
  smallLabel = false,
  hideTags = false,
}: MultiSelectAutocompleteProps): JSX.Element => {
  const { setFieldValue, handleChange, setFieldTouched } =
    useFormikContext<any>()
  const [field, meta] = useField(fieldName)
  const [searchField, searchMeta] = useField(`search-${fieldName}`)

  const containerRef = useRef<HTMLDivElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (
        !containerRef.current?.contains(e.target as Node) &&
        searchField.value !== ''
      ) {
        setIsOpen(false)
        setFieldValue(`search-${fieldName}`, '', false)
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
    const regExp = new RegExp(searchField.value, 'i')
    setFilteredOptions(
      options.filter(
        option => searchField.value === '' || option.label.match(regExp)
      )
    )
  }, [searchField.value])

  const optionsLabelById = useMemo(
    () =>
      options.reduce<Record<string, string>>((optionsById, option) => {
        optionsById[option.value] = option.label
        return optionsById
      }, {}),
    [options]
  )

  const toggleField = () => {
    if (isOpen) {
      setIsOpen(false)
      setFieldValue(`search-${fieldName}`, '', false)
    } else {
      setIsOpen(true)
    }
    setFieldTouched(fieldName, true)
  }

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={meta.touched && !meta.error ? true : hideFooter}
      isOptional={isOptional}
      label={label}
      name={`search-${fieldName}`}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
    >
      <div
        className={cx(styles['multi-select-autocomplete-container'], className)}
        ref={containerRef}
      >
        <BaseInput
          onFocus={() => {
            if (!isOpen) {
              setIsOpen(true)
            }
            setFieldTouched(fieldName, true)
          }}
          placeholder={field.value.length > 1 ? pluralLabel : label}
          style={{ paddingLeft: field.value.length > 0 ? '2.2rem' : '1rem' }}
          className={cx({
            [styles['multi-select-autocomplete-placeholder-input']]:
              field.value.length > 0,
          })}
          hasError={searchMeta.touched && !!searchMeta.error}
          type="text"
          {...searchField}
        />
        <AutocompleteList
          onButtonClick={toggleField}
          isOpen={isOpen}
          filteredOptions={filteredOptions}
          displayNumberOfSelectedValues={field.value.length > 0}
          numberOfSelectedOptions={field.value.length}
          renderOption={({ value, label }) => (
            <BaseCheckbox
              label={label}
              key={`${fieldName}-${value}`}
              value={value}
              name={fieldName}
              onChange={e => {
                setFieldTouched(`search-${fieldName}`, true)
                handleChange(e)
                onChange?.(e)
              }}
              checked={field.value.includes(value)}
            />
          )}
        />
      </div>
      {!hideTags && field.value.length > 0 && (
        <div className={styles['multi-select-autocomplete-tags']}>
          {field.value.map((value: string) => (
            <Tag
              key={`tag-${fieldName}-${value}`}
              label={optionsLabelById[value]}
              closeable={{
                onClose: () => {
                  setFieldValue(
                    fieldName,
                    field.value.filter((_value: string) => _value !== value)
                  )
                },
              }}
            />
          ))}
        </div>
      )}
    </FieldLayout>
  )
}

export default MultiSelectAutocomplete
