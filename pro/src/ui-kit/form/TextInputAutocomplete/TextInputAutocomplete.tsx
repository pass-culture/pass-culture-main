import cn from 'classnames'
import { useField, useFormikContext } from 'formik'
import { debounce } from 'lodash'
import React, { useCallback, useEffect, useRef, useState } from 'react'

import { SelectOption } from 'custom_types/form'

import {
  AutocompleteList,
  BaseCheckbox,
  BaseInput,
  FieldLayout,
} from '../shared'
import { AutocompleteItemProps } from '../shared/AutocompleteList/type'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import styles from './TextInputAutocomplete.module.scss'

export type TextInputAutocompleteProps = FieldLayoutBaseProps & {
  disabled?: boolean
  filterLabel?: string
  getSuggestions: (search: string) => Promise<AutocompleteItemProps[]>
  maxDisplayOptions?: number
  maxDisplayOptionsLabel?: string
  maxHeight?: number
  onSelectCustom?: (selectedItem: AutocompleteItemProps) => void
  onSearchChange?: () => void
  placeholder?: string
  hideArrow?: boolean
  useDebounce?: boolean
}

const AutocompleteTextInput = ({
  className,
  disabled = false,
  name,
  getSuggestions,
  hideFooter = false,
  isOptional = false,
  label,
  maxHeight = 100,
  onSelectCustom,
  smallLabel = false,
  placeholder,
  useDebounce = false,
}: TextInputAutocompleteProps): JSX.Element => {
  const [suggestions, setSuggestions] = useState<SelectOption[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isFocus, setIsFocus] = useState(false)

  const containerRef = useRef<HTMLDivElement>(null)

  const [field, meta, helpers] = useField(name)
  const [searchField] = useField({
    name: `search-${name}`,
  })
  const [lastSelectedValue, setLastSelectedValue] =
    useState<AutocompleteItemProps>()

  const { setFieldValue, setFieldTouched } = useFormikContext()

  const updateSuggestions = useCallback(
    async (search: string) => {
      const suggestions = await getSuggestions(search)
      if (suggestions.length > 0) {
        setSuggestions(suggestions)
        if (isFocus) {
          setIsOpen(true)
        }
      } else {
        setIsOpen(false)
      }
    },
    [isFocus]
  )

  const debouncedSearch = useCallback(debounce(updateSuggestions, 300), [
    isFocus,
  ])

  const handleSearchChange = useCallback(
    (search: string) => {
      if (useDebounce) {
        debouncedSearch(search)
      } else {
        updateSuggestions(search)
      }

      if (!search) {
        setIsOpen(false)
      }
      setFieldValue(`search-${name}`, search, false)
    },
    [updateSuggestions, debouncedSearch]
  )

  const updateFieldWithSelectedItem = (
    selectedItem?: AutocompleteItemProps
  ) => {
    if (onSelectCustom && selectedItem) {
      onSelectCustom(selectedItem)
    }
    helpers.setValue(selectedItem?.label || '')
    setFieldValue(`search-${name}`, selectedItem?.label || '', false)
  }
  const handleSelect = (selectedItem: AutocompleteItemProps) => {
    setLastSelectedValue(selectedItem)
    updateFieldWithSelectedItem(selectedItem)
    setIsOpen(false)
    setIsFocus(false)
  }

  const renderSuggestion = (item: SelectOption, disabled?: boolean) => (
    <BaseCheckbox
      label={item.label}
      key={`${name}-${item.value}`}
      className={cn(styles['option'], {
        [styles['option-disabled']]: disabled,
      })}
      value={item.label}
      id={`${name}-${item.value}`}
      name={`${name}-${item.value}`}
      role="option"
      aria-selected={field.value === item.label}
      disabled={disabled}
      checked={field.value === item.value}
      onClick={() => handleSelect(item)}
      readOnly
    />
  )
  const handleClickOutside = useCallback(
    (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        if (isOpen || !searchField.value) {
          updateFieldWithSelectedItem(lastSelectedValue)
          setIsOpen(false)
          setFieldTouched(name)
        }
        setIsFocus(false)
      }
    },
    [isOpen, lastSelectedValue, updateFieldWithSelectedItem]
  )

  useEffect(() => {
    if (containerRef.current) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [containerRef, handleClickOutside])

  return (
    <FieldLayout
      label={label}
      name={`search-${name}`}
      error={meta.error}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      isOptional={isOptional}
      hideFooter={hideFooter}
      className={className}
    >
      <div
        className={cn(styles['input-autocomplete-container'], className)}
        ref={containerRef}
      >
        <BaseInput
          onFocus={() => {
            setIsFocus(true)
            if (suggestions.length > 0) {
              setIsOpen(true)
            }
          }}
          placeholder={placeholder ?? label}
          hasError={meta.touched && !!meta.error}
          type="text"
          disabled={disabled}
          className={styles['select-autocomplete-input']}
          autoComplete="off"
          {...searchField}
          onChange={e => handleSearchChange(e.target.value)}
        />
        <AutocompleteList
          className={styles['menu']}
          filteredOptions={suggestions}
          hideArrow={true}
          isOpen={isOpen}
          maxHeight={maxHeight}
          onButtonClick={() => {}}
          renderOption={renderSuggestion}
        />
      </div>
    </FieldLayout>
  )
}

export default AutocompleteTextInput
