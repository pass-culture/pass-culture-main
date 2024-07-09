import cx from 'classnames'
import { useField, useFormikContext } from 'formik'
import React, { KeyboardEventHandler, useEffect, useRef, useState } from 'react'

import { SelectOption } from 'custom_types/form'
import { getLabelString } from 'utils/getLabelString'

import { BaseInput } from '../shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import { OptionsList } from './OptionsList/OptionsList'
import styles from './SelectAutocomplete.module.scss'
import { SelectedValuesTags } from './SelectedValuesTags/SelectedValuesTags'
import { Toggle } from './Toggle/Toggle'

export type SelectAutocompleteProps = FieldLayoutBaseProps & {
  disabled?: boolean
  hideArrow?: boolean
  hideTags?: boolean
  isOptional?: boolean
  maxHeight?: number
  multi?: boolean
  options: SelectOption[]
  placeholder?: string
  pluralLabel?: string
  resetOnOpen?: boolean
  onSearch?: (pattern: string) => void
  searchInOptions?: (options: SelectOption[], pattern: string) => SelectOption[]
  onReset?: () => void
  type?: 'text' | 'search'
  leftIcon?: string
  maxDisplayedOptions?: number
}

export const SelectAutocomplete = ({
  className,
  disabled = false,
  name,
  hideArrow,
  hideFooter = false,
  hideTags = false,
  inline,
  isOptional = false,
  label,
  multi = false,
  options,
  placeholder,
  pluralLabel,
  smallLabel = false,
  resetOnOpen = true,
  description,
  onSearch = () => {},
  searchInOptions = (options, pattern) =>
    options.filter((opt) =>
      opt.label.toLowerCase().includes(pattern.trim().toLowerCase())
    ),
  onReset = () => {},
  type = 'text',
  leftIcon,
  maxDisplayedOptions,
}: SelectAutocompleteProps): JSX.Element => {
  const { setFieldTouched, setFieldValue } = useFormikContext<any>()

  const [field, meta] = useField<string | string[]>(name)
  const [searchField, searchMeta] = useField(`search-${name}`)

  const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
    null
  )
  const [optionsLabelById, setOptionsLabelById] = useState<
    Record<string, string>
  >({})
  const containerRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLUListElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    const resetSearchField = async () => {
      await setFieldValue(`search-${name}`, '', false)
      await setFieldValue(name, multi ? [] : '', false)
      onReset()
    }
    if (isOpen && resetOnOpen && searchField.value !== '') {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      resetSearchField()
    }
  }, [isOpen])

  /* hashtable for the options */
  useEffect(() => {
    setOptionsLabelById(
      options.reduce<Record<string, string>>((optionsById, option) => {
        optionsById[option.value] = option.label
        return optionsById
      }, {})
    )
  }, [options])

  /* istanbul ignore next */
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
    onSearch(searchField.value.trim())

    setHoveredOptionIndex(null)
  }, [searchField.value])

  useEffect(() => {
    setFilteredOptions(searchInOptions(options, searchField.value))
  }, [searchField.value, options])

  /* istanbul ignore next: DEBT TO FIX */
  const handleKeyDown: KeyboardEventHandler<HTMLDivElement> = async (event) => {
    /* istanbul ignore next */
    switch (event.key) {
      case 'ArrowUp':
        if (hoveredOptionIndex !== null) {
          if (hoveredOptionIndex <= 0) {
            setHoveredOptionIndex(null)
          } else {
            setHoveredOptionIndex(hoveredOptionIndex - 1)
          }
        }
        if (!isOpen) {
          setIsOpen(true)
        }
        listRef.current?.focus()
        break
      case 'ArrowDown':
        if (hoveredOptionIndex === null) {
          if (filteredOptions.length > 0) {
            setHoveredOptionIndex(0)
          }
        } else if (hoveredOptionIndex >= filteredOptions.length - 1) {
          setHoveredOptionIndex(filteredOptions.length - 1)
        } else {
          setHoveredOptionIndex(hoveredOptionIndex + 1)
        }
        if (!isOpen) {
          setIsOpen(true)
        }
        listRef.current?.focus()
        break
      case 'Space':
        await openField()
        listRef.current?.focus()
        break
      case 'Enter':
        if (isOpen && hoveredOptionIndex !== null) {
          event.preventDefault()
          await selectOption(String(filteredOptions[hoveredOptionIndex].value))
        }
        break
      case 'Escape':
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      case 'Tab':
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      default:
        //
        break
    }
  }

  const selectOption = async (value: string) => {
    let updatedSelection
    if (multi) {
      if (field.value.includes(value) && Array.isArray(field.value)) {
        updatedSelection = field.value.filter((li) => li !== value)
      } else {
        updatedSelection = [...field.value, value]
      }
    } else {
      updatedSelection = value
      setIsOpen(false)
      setHoveredOptionIndex(null)
      await setFieldValue(
        `search-${name}`,
        optionsLabelById[updatedSelection],
        false
      )
    }
    await setFieldValue(name, updatedSelection)
  }

  const openField = async () => {
    /* istanbul ignore next */
    if (!isOpen) {
      setIsOpen(true)
    }
    await setFieldTouched(name, true)
  }

  const toggleField = async () => {
    if (isOpen) {
      setIsOpen(false)
      await setFieldValue(`search-${name}`, '', false)
    } else {
      setIsOpen(true)
    }
    await setFieldTouched(name, true)
  }

  const placeholderDisplay = Array.isArray(field.value)
    ? placeholder ??
      (field.value.length > 1 && pluralLabel ? pluralLabel : label)
    : placeholder ?? optionsLabelById[field.value]

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      hideFooter={!hideTags && hideFooter}
      isOptional={isOptional}
      label={label}
      name={`search-${name}`}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      inline={inline}
      description={description}
    >
      <div
        className={cx(styles['multi-select-autocomplete-container'], className)}
        onKeyDown={handleKeyDown}
        ref={containerRef}
      >
        <BaseInput
          {...(hoveredOptionIndex !== null && {
            'aria-activedescendant': `option-display-${filteredOptions[hoveredOptionIndex]?.value}`,
          })}
          onFocus={openField}
          placeholder={getLabelString(placeholderDisplay)}
          style={{
            paddingLeft:
              (multi && field.value.length > 0) || leftIcon ? '2.2rem' : '1rem',
          }}
          className={styles['multi-select-autocomplete-placeholder-input']}
          hasError={searchMeta.touched && !!meta.error}
          type={type}
          disabled={disabled}
          {...searchField}
          aria-autocomplete="list"
          aria-controls={`list-${name}`}
          aria-describedby={`help-${name}`}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-required={!isOptional}
          role="combobox"
          leftIcon={leftIcon}
        />
        <div
          aria-live="polite"
          aria-relevant="text"
          className="visually-hidden"
          id={`help-${name}`}
        >
          {multi && `${field.value.length} options sélectionnées`}
          {!multi &&
            !Array.isArray(field.value) &&
            field.value !== '' &&
            `Option sélectionnée : ${optionsLabelById[field.value]}`}
          {isOpen
            ? `${filteredOptions.length} options ${
                searchField.value === ''
                  ? 'disponibles'
                  : 'correspondant au texte saisi'
              }`
            : 'saisissez du texte pour afficher et filtrer les options'}
        </div>
        <select
          hidden
          {...(multi && { multiple: true })}
          {...field}
          value={field.value || ''}
          data-testid="select"
        >
          {options.map(({ label, value }) => (
            <option key={`option-${value}`} value={value}>
              {label}
            </option>
          ))}
        </select>
        <div className={styles['field-overlay']}>
          {!hideArrow && (
            <Toggle
              disabled={disabled}
              isOpen={isOpen}
              toggleField={toggleField}
            />
          )}
          {multi && field.value.length > 0 && (
            <div onClick={toggleField} className={styles['pellet']}>
              {field.value.length}
            </div>
          )}
          {isOpen && (
            <OptionsList
              className={className}
              fieldName={name}
              selectedValues={field.value}
              filteredOptions={filteredOptions}
              setHoveredOptionIndex={setHoveredOptionIndex}
              listRef={listRef}
              hoveredOptionIndex={hoveredOptionIndex}
              selectOption={selectOption}
              multi={multi}
              maxDisplayedOptions={maxDisplayedOptions}
            />
          )}
        </div>
      </div>
      {Array.isArray(field.value) && !hideTags && field.value.length > 0 && (
        <SelectedValuesTags
          disabled={disabled}
          fieldName={name}
          optionsLabelById={optionsLabelById}
          selectedOptions={field.value}
          removeOption={selectOption}
        />
      )}
    </FieldLayout>
  )
}
