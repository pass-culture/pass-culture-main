import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useField, useFormikContext } from 'formik'

import BaseCheckbox from '../shared/BaseCheckbox'
import FieldLayout from '../shared/FieldLayout'
import Icon from 'components/layout/Icon'
import { SelectOption } from 'custom_types/form'
import Tag from 'ui-kit/Tag'
import TextInput from '../TextInput'
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
  const { values, setFieldValue, handleChange, setFieldTouched } = useFormikContext<any>()
  const [field, meta] = useField(fieldName)

  const containerRef = useRef<HTMLDivElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)
  const { [`search-${fieldName}`]: searched } = values

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
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
    const regExp = new RegExp(searched, 'i')
    setFilteredOptions(
      options.filter(option => searched === '' || option.label.match(regExp))
    )
  }, [searched])

  const optionsLabelById = useMemo(
    () =>
      options.reduce<Record<string, string>>((optionsById, option) => {
        optionsById[option.value] = option.label
        return optionsById
      }, {}),
    [options]
  )

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={hideFooter}
      isOptional={isOptional}
      label="" // to avoid duplicated label, included in MultiSelectAutocomplete
      name={fieldName}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
    >
      <div
        className={cx(styles['multi-select-autocomplete-container'], className)}
        ref={containerRef}
      >
        <TextInput
          hideFooter
          label={label}
          onFocus={() => {
            if (!isOpen) {setIsOpen(true)}
            setFieldTouched(fieldName, true)
          }}
          name={`search-${fieldName}`}
          placeholder={field.value.length > 1 ? pluralLabel : label}
          style={{ paddingLeft: field.value.length > 0 ? '2.2rem' : '1rem' }}
        />
        <div className={styles['field-overlay']}>
          <button
            onClick={() => {
              if (isOpen) {
                setIsOpen(false)
                setFieldValue(`search-${fieldName}`, '', false)
              } else {
                setIsOpen(true)
              }
              setFieldTouched(fieldName, true)
            }}
            className={cx(styles['dropdown-indicator'], {
              [styles['dropdown-indicator-is-closed']]: !isOpen,
            })}
            type="button"
          >
            <Icon
              svg="open-dropdown"
              alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
            />
          </button>
          {field.value.length > 0 && (
            <div className={styles['pellet']}>{field.value.length}</div>
          )}
          {isOpen && (
            <div
              className={cx(styles['multi-select-autocomplete__menu'], {
                [styles['multi-select-autocomplete__menu--no-results']]:
                  filteredOptions.length === 0,
              })}
            >
              {filteredOptions.length === 0 && 'Aucun résultat'}
              {filteredOptions.map(({ value, label }) => (
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
              ))}
            </div>
          )}
        </div>
      </div>
      {!hideTags && field.value.length > 0 && (
        <div className={styles['multi-select-autocomplete-tags']}>
          {values[fieldName].map((value: string) => (
            <Tag
              label={optionsLabelById[value]}
              closeable={{
                onClose: e => {
                  setFieldValue(
                    fieldName,
                    values[fieldName].filter(
                      (_value: string) => _value !== value
                    )
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
