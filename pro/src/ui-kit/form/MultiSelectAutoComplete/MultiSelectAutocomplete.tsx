import cx from 'classnames'
import { useField, useFormikContext } from 'formik'
import React, { useEffect, useMemo, useRef, useState } from 'react'

import { SelectOption } from 'custom_types/form'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { getLabelString } from 'utils/getLabelString'

import { SelectedValuesTags } from '../SelectAutoComplete/SelectedValuesTags/SelectedValuesTags'
import { BaseInput } from '../shared'
import AutocompleteList from '../shared/AutocompleteList'
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
  filterMaxLength?: number
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
  filterMaxLength = 255,
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
    async function setSearch() {
      if (!isOpen && searchField.value !== '') {
        await setFieldValue(`search-${name}`, '', false)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setSearch()
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
        (option) =>
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

  const toggleField = async () => {
    if (isOpen) {
      setIsOpen(false)
      await setFieldValue(`search-${name}`, '', false)
    } else {
      setIsOpen(true)
    }
    await setFieldTouched(name, true)
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
          onFocus={async () => {
            if (!isOpen) {
              setIsOpen(true)
            }
            await setFieldTouched(name, true)
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
          maxLength={filterMaxLength}
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
              onChange={(e) => {
                // Don't know why the multiselect doesn't work anymore if we await this setFieldTouched
                void setFieldTouched(`search-${name}`, true)
                handleChange(e)
                onChange?.(e)
              }}
              checked={field.value.includes(value)}
            />
          )}
        />
      </div>

      {!hideTags && field.value.length > 0 && (
        <SelectedValuesTags
          disabled={disabled}
          fieldName={name}
          optionsLabelById={optionsLabelById}
          selectedOptions={field.value}
          removeOption={(value) =>
            setFieldValue(
              name,
              field.value.filter((_value: string) => _value !== value)
            )
          }
        />
      )}
    </FieldLayout>
  )
}

export default MultiSelectAutocomplete
