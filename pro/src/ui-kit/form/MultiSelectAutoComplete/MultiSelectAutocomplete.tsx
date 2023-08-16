import cx from 'classnames'
import { useField, useFormikContext } from 'formik'
import React, { useEffect, useMemo, useRef, useState } from 'react'

import { SelectOption } from 'custom_types/form'
import Tag from 'ui-kit/Tag'
import { getLabelString } from 'utils/getLabelString'

import { BaseInput } from '../shared'
import AutocompleteList from '../shared/AutocompleteList'
import BaseCheckbox from '../shared/BaseCheckbox'
import FieldLayout from '../shared/FieldLayout'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import styles from './MultiSelectAutocomplete.module.scss'

export type MultiSelectAutocompleteProps = FieldLayoutBaseProps & {
  hideTags?: boolean
  maxDisplayOptions?: number
  maxDisplayOptionsLabel?: string
  maxHeight?: number
  options: SelectOption[]
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  pluralLabel?: string
  disabled?: boolean
  placeholder?: string
}

const MultiSelectAutocomplete = ({
  className,
  name,
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
}: MultiSelectAutocompleteProps): JSX.Element => {
  const { setFieldValue, handleChange, setFieldTouched } =
    useFormikContext<any>()
  const [field, meta] = useField(name)
  const [searchField, searchMeta] = useField(`search-${name}`)

  const containerRef = useRef<HTMLDivElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    if (!isOpen && searchField.value !== '') {
      setFieldValue(`search-${name}`, '', false)
    }
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
    setFilteredOptions(
      options.filter(
        option =>
          searchField.value === '' ||
          option.label
            .toLocaleLowerCase()
            .includes(searchField.value.toLocaleLowerCase())
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
      setFieldValue(`search-${name}`, '', false)
    } else {
      setIsOpen(true)
    }
    setFieldTouched(name, true)
  }

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={!hideTags && field.value.length > 0 ? true : hideFooter}
      isOptional={isOptional}
      label={label}
      name={`search-${name}`}
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
            setFieldTouched(name, true)
          }}
          placeholder={
            placeholder ??
            (field.value.length > 1 && pluralLabel
              ? pluralLabel
              : getLabelString(label))
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
        <AutocompleteList
          disabled={disabled}
          onButtonClick={toggleField}
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
          maxHeight={maxHeight}
          displayNumberOfSelectedValues={field.value.length > 0}
          numberOfSelectedOptions={field.value.length}
          renderOption={({ value, label }) => (
            <BaseCheckbox
              label={label}
              key={`${name}-${value}`}
              value={value}
              name={name}
              onChange={e => {
                setFieldTouched(`search-${name}`, true)
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
              key={`tag-${name}-${value}`}
              label={optionsLabelById[value]}
              closeable={{
                onClose: () => {
                  setFieldValue(
                    name,
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

export default MultiSelectAutocomplete
