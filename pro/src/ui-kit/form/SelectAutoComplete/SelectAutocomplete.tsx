import classNames from 'classnames'
import {
  type ForwardedRef,
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import { noop } from '@/commons/utils/noop'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import { OptionsList } from './OptionsList/OptionsList'
import styles from './SelectAutocomplete.module.scss'
import { Toggle } from './Toggle/Toggle'

export type CustomEvent<T extends 'change' | 'blur'> = {
  type: T
  target: { name: string; value: string }
}

/**
 * Base props for the SelectAutocomplete component
 */
type CommonProps = {
  /** Name of the field, used for form submission and accessibility */
  name: string
  /** Label displayed above the input */
  label: string | JSX.Element
  /** List of available options */
  options: SelectOption[]

  /** Helper text displayed below the input */
  description?: string
  /** Disables the input and prevents interaction */
  disabled?: boolean
  /** Indicates if the field is required */
  required?: boolean
  /** Additional CSS class names */
  className?: string
  /** Error message to display */
  error?: string
  /** Hides the dropdown arrow */
  hideArrow?: boolean
  /** Called when the selected value changes */
  onChange?(e: CustomEvent<'change'>): void
  /** Called when the input loses focus */
  onBlur?(e: CustomEvent<'blur'>): void
  /** Value of the input */
  value?: string
  /** Called when the search input changes */
  onSearch?(pattern: string): void
  /** Custom function to filter options based on search pattern */
  searchInOptions?(options: SelectOption[], pattern: string): SelectOption[]
}

/**
 * Props for when resetOnOpen is true
 */
type WithResetOnOpen = {
  /** Resets the input value when dropdown opens. */
  resetOnOpen?: true
  /** Called when the input is reset. */
  onReset?(): void
}

/**
 * Props for when resetOnOpen is false
 */
type WithoutResetOnOpen = {
  resetOnOpen?: false
  /** (cannot be provided when `resetOnOpen` is `false`) */
  onReset?: never
}

export type SelectAutocompleteProps =
  | (CommonProps & WithResetOnOpen)
  | (CommonProps & WithoutResetOnOpen)

export const SelectAutocomplete = forwardRef(
  (
    {
      className,
      disabled = false,
      name,
      hideArrow,
      required = true,
      label,
      options,
      resetOnOpen = true,
      description,
      error,
      onChange = () => noop,
      onBlur = () => noop,
      value: inputValue,
      onSearch = () => noop,
      searchInOptions = (options, pattern) =>
        options.filter((opt) =>
          opt.label.toLowerCase().includes(pattern.trim().toLowerCase())
        ),
      onReset = () => noop,
    }: SelectAutocompleteProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const [searchField, setSearchField] = useState('') // Represents the <input type="search"> value while typing (e.g. "Alpes de Ha…")
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
      null
    ) // Represents the index of the hovered option while using keyboard (for a11y), useful for the "aria-activedescendant" attribute

    const optionsLabelById = useRef<Map<string, string>>() // Hashtables for the options (ex: "05" -> "Hautes-Alpes")
    const optionsIdByLabel = useRef<Map<string, string>>() // Inverted hashtables for the labels (ex: "Hautes-Alpes" -> "05")
    const hasComponentFirstRendered = useRef(false)
    const containerRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null) // Ref for "searchField"
    const listRef = useRef<HTMLUListElement>(null) // Ref for <ul> dropdown

    // Hydrates the hashtables (computed at 1st render only)
    useEffect(() => {
      // We need to cast "as string" because SelectOption[] type is "string | number", but here it'll be always treated as a string
      optionsLabelById.current = new Map(
        options.map(({ label, value }) => [value as string, label])
      )
      optionsIdByLabel.current = new Map(
        options.map(({ label, value }) => [label, value as string])
      )
    }, [options])

    // Handles "resetOnOpen" behavior
    useEffect(() => {
      if (resetOnOpen && isDropdownOpen) {
        setSearchField('')
        onReset()
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isDropdownOpen, resetOnOpen])

    // Clicking outside the container will close the dropdown
    useEffect(() => {
      const handleClickOutside = (e: MouseEvent): void => {
        if (!containerRef.current?.contains(e.target as Node)) {
          setIsDropdownOpen(false)
        }
      }
      if (containerRef.current) {
        document.addEventListener('mousedown', handleClickOutside)
      }
      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [containerRef])

    // Handle "onSearch" prop for parent which may want to get the searchField information
    useEffect(() => {
      setHoveredOptionIndex(null)

      // Necessary to not trigger "onSearch" at first render
      if (!hasComponentFirstRendered.current) {
        hasComponentFirstRendered.current = true
        return
      }

      onSearch(searchField.trim())
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchField])

    // Compute options filter by search, using the default `searchInOptions` function (or a custom one, if provided via the props)
    const filteredOptions = searchInOptions(options, searchField)

    // Handles keyboard navigation when the dropdown is open
    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
      switch (event.key) {
        case 'ArrowUp':
          if (hoveredOptionIndex !== null) {
            event.preventDefault()

            //  Activate and scroll to the previous element in the list
            const newIndex =
              (hoveredOptionIndex - 1 + filteredOptions.length) %
              filteredOptions.length

            setHoveredOptionIndex(newIndex)
            const nextHoveredElement =
              listRef.current?.getElementsByTagName('li')[newIndex]
            nextHoveredElement?.scrollIntoView({ block: 'nearest' })
          }
          break
        case 'ArrowDown':
          openDropdown()
          if (hoveredOptionIndex === null) {
            if (filteredOptions.length > 0) {
              setHoveredOptionIndex(0)
            }
          } else {
            //  Activate and scroll to the next element in the list
            const newIndex = (hoveredOptionIndex + 1) % filteredOptions.length

            setHoveredOptionIndex(newIndex)
            const nextHoveredElement =
              listRef.current?.getElementsByTagName('li')[newIndex]
            nextHoveredElement?.scrollIntoView({ block: 'nearest' })
          }
          break
        case 'Enter':
          if (
            isDropdownOpen &&
            hoveredOptionIndex !== null &&
            filteredOptions[hoveredOptionIndex]
          ) {
            event.preventDefault()
            if (filteredOptions[hoveredOptionIndex]) {
              selectOption(String(filteredOptions[hoveredOptionIndex].value))
            }
          }
          break
        case 'Escape':
          event.preventDefault()
          if (isDropdownOpen) {
            setHoveredOptionIndex(null)
            setIsDropdownOpen(false)
          } else {
            setSearchField('')
          }
          break
        case 'Tab':
          setHoveredOptionIndex(null)
          setIsDropdownOpen(false)
          break
        default:
          break
      }
    }

    // When an option is chosen
    const selectOption = (value: string) => {
      setSearchField(optionsLabelById.current?.get(value) ?? '')

      // Notify changes up to the parent component
      onChange({ type: 'change', target: { name, value } })
      onBlur({ type: 'blur', target: { name, value } })

      setIsDropdownOpen(false)
      setHoveredOptionIndex(null)
    }

    const openDropdown = () => {
      if (!isDropdownOpen) {
        setIsDropdownOpen(true)
      }
    }

    const toggleDropdown = () => {
      if (!isDropdownOpen) {
        setIsDropdownOpen(true)
      } else {
        setIsDropdownOpen(false)
      }
      inputRef.current?.focus()
    }

    // When the inputRef's value changes externally
    useEffect(() => {
      // get the value from either the "value" prop or via the inputRef
      const externalValue =
        (inputValue || (ref && inputRef.current?.value)) ?? ''

      // associate the new value to the good label in the "searchField" (ex: "05" -> "Hautes-Alpes")
      // fallback to the external value if the inputRef's value is not in the options
      setSearchField(
        optionsLabelById.current?.get(externalValue) ?? externalValue
      )
    }, [inputRef, inputValue, ref])

    // Connect the external reference to the internal one "inputRef", so we can read it's value in the "useEffect" above
    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <FieldLayout
        className={className}
        error={error}
        required={required}
        label={label}
        name={name}
        showError={!!error}
        description={description}
      >
        <div
          className={classNames(
            styles['multi-select-autocomplete-container'],
            className
          )}
          ref={containerRef}
        >
          {/* Search field */}
          <input
            {...(hoveredOptionIndex !== null && {
              'aria-activedescendant': `option-display-${filteredOptions[hoveredOptionIndex]?.value}`,
            })}
            onClick={openDropdown}
            className={classNames(
              styles['multi-select-autocomplete-placeholder-input'],
              {
                [styles['has-error']]: Boolean(error),
              }
            )}
            onKeyDown={handleKeyDown}
            type="search"
            disabled={disabled}
            aria-autocomplete="list"
            aria-controls={`list-${name}`}
            id={name}
            aria-expanded={isDropdownOpen}
            aria-haspopup="listbox"
            aria-required={required}
            role="combobox"
            value={searchField}
            ref={inputRef}
            name={name}
            onChange={(e) => {
              setHoveredOptionIndex(null)
              setSearchField(e.target.value)

              onChange({
                type: 'change',
                target: { name, value: e.target.value },
              })
              openDropdown()
            }}
            onBlur={(e) => {
              setSearchField(e.target.value)

              // Check if value is part of the hashtable before notify the parent
              // This is necessary because user can type anything in the "searchField" and then "blur" the field
              // If the specified value isn't in the valid options hastable, we send an empty string instead and let the parent deal with it
              const value = optionsIdByLabel.current?.get(e.target.value) ?? ''

              onBlur({
                type: 'blur',
                target: { name, value },
              })
            }}
          />

          {/* Dropdown options list */}
          <div className={styles['field-overlay']}>
            {!hideArrow && (
              <Toggle
                disabled={disabled}
                isOpen={isDropdownOpen}
                toggleField={toggleDropdown}
              />
            )}
            {isDropdownOpen && (
              <OptionsList
                className={className}
                fieldName={name}
                filteredOptions={filteredOptions}
                setHoveredOptionIndex={setHoveredOptionIndex}
                listRef={listRef}
                hoveredOptionIndex={hoveredOptionIndex}
                selectOption={selectOption}
              />
            )}
          </div>
        </div>
      </FieldLayout>
    )
  }
)

SelectAutocomplete.displayName = 'SelectAutocomplete'
