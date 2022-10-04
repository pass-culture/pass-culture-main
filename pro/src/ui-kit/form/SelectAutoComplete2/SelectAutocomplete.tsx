import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useField, useFormikContext } from 'formik'

import BaseCheckbox from '../shared/BaseCheckbox'
import { BaseInput } from '../shared'
import FieldLayout from '../shared/FieldLayout'
import Icon from 'components/layout/Icon'
import { SelectOption } from 'custom_types/form'
import Tag from 'ui-kit/Tag'
import cx from 'classnames'
import styles from './SelectAutocomplete.module.scss'

export interface SelectAutocompleteProps {
  className?: string
  fieldName: string
  hideFooter?: boolean
  hideTags?: boolean
  isOptional?: boolean
  label: string
  maxDisplayOptions?: number
  maxDisplayOptionsLabel?: string
  maxHeight?: number
  options: SelectOption[]
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  pluralLabel?: string
  smallLabel?: boolean
  disabled?: boolean
  placeholder?: string
  inline?: boolean
  hideArrow?: boolean
}

const SelectAutocomplete = ({
  className,
  fieldName,
  hideFooter = false,
  hideTags = false,
  isOptional = false,
  label,
  options,
  onChange,
  maxDisplayOptions,
  maxHeight,
  pluralLabel,
  smallLabel = false,
  disabled = false,
  placeholder,
  inline,
  hideArrow,
}: SelectAutocompleteProps): JSX.Element => {
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
    if (!isOpen && searchField.value !== '')
      setFieldValue(`search-${fieldName}`, '', false)
  }, [isOpen])

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

  const renderOption = ({ value, label }) => (
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
  )

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={!hideTags && field.value.length > 0 ? true : hideFooter}
      isOptional={isOptional}
      label={label}
      name={`search-${fieldName}`}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      inline={inline}
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
          placeholder={
            placeholder ??
            (field.value.length > 1 && pluralLabel ? pluralLabel : label)
          }
          style={{ paddingLeft: field.value.length > 0 ? '2.2rem' : '1rem' }}
          className={cx({
            [styles['multi-select-autocomplete-placeholder-input']]:
              field.value.length > 0,
          })}
          hasError={searchMeta.touched && !!searchMeta.error}
          type="text"
          disabled={disabled}
          {...searchField}
        />
        (
        <div className={styles['field-overlay']}>
          {!hideArrow && (
            <button
              onClick={toggleField}
              className={cx(styles['dropdown-indicator'], {
                [styles['dropdown-indicator-is-closed']]: !isOpen,
              })}
              type="button"
              disabled={disabled}
            >
              <Icon
                svg="open-dropdown"
                alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
              />
            </button>
          )}
          {field.value.length > 0 && (
            <div onClick={toggleField} className={styles['pellet']}>
              {field.value.length}
            </div>
          )}
          {isOpen && (
            <div
              className={cx(styles['menu'], className)}
              style={maxHeight ? { maxHeight } : {}}
              role="listbox"
            >
              {filteredOptions.length === 0 && (
                <span
                  className={cx({
                    [styles['menu--no-results']]: filteredOptions.length === 0,
                  })}
                >
                  Aucun résultat
                </span>
              )}
              {filteredOptions.map(option => renderOption(option))}
            </div>
          )}
        </div>
        )
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
                disabled,
              }}
            />
          ))}
        </div>
      )}
    </FieldLayout>
  )
}

export default SelectAutocomplete
