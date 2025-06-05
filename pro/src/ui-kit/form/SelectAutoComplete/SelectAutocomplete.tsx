import cx from 'classnames'
import { useField, useFormikContext } from 'formik'
import { KeyboardEventHandler, useEffect, useRef, useState } from 'react'

import { SelectOption } from 'commons/custom_types/form'

import { SelectedValuesTags } from '../../SelectedValuesTags/SelectedValuesTags'
import { BaseInput } from '../shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import { OptionsList } from './OptionsList/OptionsList'
import styles from './SelectAutocomplete.module.scss'
import { Toggle } from './Toggle/Toggle'

export type SelectAutocompleteProps = FieldLayoutBaseProps & {
  disabled?: boolean
  hideArrow?: boolean
  hideTags?: boolean
  isOptional?: boolean
  maxHeight?: number
  multi?: boolean
  options: SelectOption[]
  resetOnOpen?: boolean
  onSearch?: (pattern: string) => void
  searchInOptions?: (options: SelectOption[], pattern: string) => SelectOption[]
  onReset?: () => void
  maxDisplayedOptions?: number
  selectedValuesTagsClassName?: string
  /**
   * A flag to automatically focus the input when the component mounts.
   */
  shouldFocusOnMount?: boolean
  /**
   * A flag to prevent the dropdown from opening on the first focus.
   * This is useful when the input is automatically focused. The user
   * is then expected to open the dropdown by clicking on the input.
   */
  preventOpenOnFirstFocus?: boolean
}

export const SelectAutocomplete = ({
  className,
  selectedValuesTagsClassName,
  disabled = false,
  name,
  hideArrow,
  hideTags = false,
  inline,
  isOptional = false,
  label,
  multi = false,
  options,
  resetOnOpen = true,
  description,
  onSearch = () => {},
  searchInOptions = (options, pattern) =>
    options.filter((opt) =>
      opt.label.toLowerCase().includes(pattern.trim().toLowerCase())
    ),
  onReset = () => {},
  maxDisplayedOptions,
  isLabelHidden,
  shouldFocusOnMount,
  preventOpenOnFirstFocus,
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
  const inputRef = useRef<HTMLInputElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)

  useEffect(() => {
    const focusOnMount = async () => {
      if (shouldFocusOnMount) {
        inputRef.current?.focus()
        await setFieldTouched(`search-${name}`, true)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    focusOnMount()
  }, [])

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
    // searchField.value can be undefined
    onSearch((searchField.value ?? '').trim())
    setHoveredOptionIndex(null)
  }, [searchField.value])

  useEffect(() => {
    setFilteredOptions(
      searchInOptions(options, (searchField.value ?? '').trim())
    )
  }, [searchField.value, options])

  const handleKeyDown: KeyboardEventHandler<HTMLDivElement> = async (event) => {
    switch (event.key) {
      case 'ArrowUp':
        if (hoveredOptionIndex !== null) {
          if (hoveredOptionIndex <= 0) {
            setHoveredOptionIndex(null)
          } else {
            //  Activate and scroll to the previous element in the list
            const newIndex = hoveredOptionIndex - 1
            setHoveredOptionIndex(newIndex)
            const nextHoveredElement =
              listRef.current?.getElementsByTagName('li')[newIndex]
            nextHoveredElement?.scrollIntoView({ block: 'nearest' })
          }
        }
        if (!isOpen) {
          setIsOpen(true)
        }
        break
      case 'ArrowDown':
        if (hoveredOptionIndex === null) {
          if (filteredOptions.length > 0) {
            setHoveredOptionIndex(0)
          }
        } else {
          //  Activate and scroll to the next element in the list
          const newIndex = Math.min(
            filteredOptions.length - 1,
            hoveredOptionIndex + 1
          )
          setHoveredOptionIndex(newIndex)
          const nextHoveredElement =
            listRef.current?.getElementsByTagName('li')[newIndex]
          nextHoveredElement?.scrollIntoView({ block: 'nearest' })
        }
        if (!isOpen) {
          setIsOpen(true)
        }
        break
      case ' ': //  Space key
      case 'Enter':
        if (
          isOpen &&
          hoveredOptionIndex !== null &&
          filteredOptions[hoveredOptionIndex]
        ) {
          event.preventDefault()
          if (filteredOptions[hoveredOptionIndex]) {
            await selectOption(
              String(filteredOptions[hoveredOptionIndex].value)
            )
          }
        }
        break
      case 'Escape':
        inputRef.current?.focus()
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      case 'Tab':
        setHoveredOptionIndex(null)
        setIsOpen(false)
        break
      default:
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

  const openFieldOnFocus = async () => {
    const focusedOnce = meta.touched
    const shouldOpen = preventOpenOnFirstFocus
      ? focusedOnce && !isOpen
      : !isOpen

    if (shouldOpen) {
      setIsOpen(true)
    }

    await setFieldTouched(name, true)
  }

  const openFieldOnClick = async () => {
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

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      name={`search-${name}`}
      showError={searchMeta.touched && !!meta.error}
      inline={inline}
      description={description}
      isLabelHidden={isLabelHidden}
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
          onClick={openFieldOnClick}
          onFocus={openFieldOnFocus}
          className={styles['multi-select-autocomplete-placeholder-input']}
          hasError={searchMeta.touched && !!meta.error}
          type="search"
          disabled={disabled}
          {...searchField}
          aria-autocomplete="list"
          aria-controls={`list-${name}`}
          aria-describedby={`help-${name}`}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-required={!isOptional}
          role="combobox"
          ref={inputRef}
        />
        <div
          aria-live="polite"
          aria-relevant="text"
          className={styles['visually-hidden']}
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
          className={selectedValuesTagsClassName}
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
