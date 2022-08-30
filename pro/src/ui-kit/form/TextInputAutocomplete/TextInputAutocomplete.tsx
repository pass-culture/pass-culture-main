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
import { IAutocompleteItemProps } from '../shared/AutocompleteList/type'

import styles from './TextInputAutocomplete.module.scss'

export interface ITextInputAutocompleteProps {
  className?: string
  disabled?: boolean
  fieldName: string
  filterLabel?: string
  getSuggestions: (search: string) => Promise<IAutocompleteItemProps[]>
  hideFooter?: boolean
  isOptional?: boolean
  label: string
  maxDisplayOptions?: number
  maxDisplayOptionsLabel?: string
  maxHeight?: number
  onSelectCustom?: (selectedItem: IAutocompleteItemProps) => void
  onSearchChange?: () => void
  smallLabel?: boolean
  placeholder?: string
  hideArrow?: boolean
  useDebounce?: boolean
}

const AutocompleteTextInput = ({
  className,
  disabled = false,
  fieldName,
  getSuggestions,
  hideFooter = false,
  isOptional = false,
  label,
  maxHeight = 100,
  onSelectCustom,
  smallLabel = false,
  placeholder,
  useDebounce = false,
}: ITextInputAutocompleteProps): JSX.Element => {
  const [suggestions, setSuggestions] = useState<SelectOption[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isFocus, setIsFocus] = useState(false)

  const containerRef = useRef<HTMLDivElement>(null)

  const [field, meta, helpers] = useField(fieldName)
  const [searchField] = useField({
    name: `search-${fieldName}`,
  })
  const [lastSelectedValue, setLastSelectedValue] =
    useState<IAutocompleteItemProps>()

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
      setFieldValue(`search-${fieldName}`, search, false)
    },
    [updateSuggestions, debouncedSearch]
  )

  const updateFieldWithSelectedItem = (
    selectedItem?: IAutocompleteItemProps
  ) => {
    if (onSelectCustom && selectedItem) {
      onSelectCustom(selectedItem)
    }
    helpers.setValue(selectedItem?.label || '')
    setFieldValue(`search-${fieldName}`, selectedItem?.label || '', false)
  }
  const handleSelect = (selectedItem: IAutocompleteItemProps) => {
    setLastSelectedValue(selectedItem)
    updateFieldWithSelectedItem(selectedItem)
    setIsOpen(false)
    setIsFocus(false)
  }

  const renderSuggestion = (item: SelectOption, disabled?: boolean) => (
    <BaseCheckbox
      label={item.label}
      key={`${fieldName}-${item.value}`}
      className={cn(styles['option'], {
        [styles['option-disabled']]: disabled,
      })}
      value={item.label}
      id={`${fieldName}-${item.value}`}
      name={`${fieldName}-${item.value}`}
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
          setFieldTouched(fieldName)
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
      name={`search-${fieldName}`}
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
