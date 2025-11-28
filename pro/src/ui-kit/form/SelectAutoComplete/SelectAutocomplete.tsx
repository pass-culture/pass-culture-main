import classNames from 'classnames'
import {
  type ForwardedRef,
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'

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
export type SelectAutocompleteProps = {
  /** Name of the field, used for form submission and accessibility */
  name: string
  /** Label displayed above the input */
  label: string | JSX.Element
  /** List of available options */
  options: string[]
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
  /** Called when the selected value changes */
  onChange?(e: CustomEvent<'change'>): void
  /** Called when the input loses focus */
  onBlur?(e: CustomEvent<'blur'>): void
  /** Value of the input */
  value?: string
  /** Custom function to filter options based on search pattern */
  searchInOptions?(options: string[], pattern: string): string[]
  /** Called when the dropdown opens */
  resetOnOpen?: boolean
}

export const SelectAutocomplete = forwardRef(
  (
    {
      className,
      disabled = false,
      name,
      required = true,
      label,
      options,
      description,
      error,
      onChange = () => noop,
      onBlur = () => noop,
      value: inputValue,
      searchInOptions = (options, pattern) =>
        options.filter((opt) =>
          opt.toLowerCase().includes(pattern.trim().toLowerCase())
        ),
      resetOnOpen = false,
    }: SelectAutocompleteProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const [searchField, setSearchField] = useState('')
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
      null
    ) // Represents the index of the hovered option while using keyboard (for a11y), useful for the "aria-activedescendant" attribute
    const containerRef = useRef<HTMLDivElement>(null) // Represents the <input type="search"> value while typing (e.g. "Alpes de Ha…")
    const inputRef = useRef<HTMLInputElement>(null) // Ref for "searchField"
    const listRef = useRef<HTMLUListElement>(null) // Ref for <ul> dropdown

    useEffect(() => {
      const externalValue = inputValue || inputRef.current?.value

      if (externalValue !== searchField) {
        setSearchField(externalValue ?? '')
        onChange({
          type: 'change',
          target: { name, value: externalValue ?? '' },
        })
      }
    }, [searchField, onChange, name, inputValue])

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
    })

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
              selectOption(filteredOptions[hoveredOptionIndex])
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
    const selectOption = (option: string) => {
      // Notify changes up to the parent component
      setSearchField(option)
      onBlur({
        type: 'blur',
        target: { name, value: option },
      })
      setHoveredOptionIndex(null)
      setIsDropdownOpen(false)
    }

    const openDropdown = () => {
      if (!isDropdownOpen) {
        setIsDropdownOpen(true)
        if (resetOnOpen) {
          setSearchField('')
          onBlur({
            type: 'blur',
            target: { name, value: '' },
          })
        }
      }
    }

    const toggleDropdown = () => {
      setIsDropdownOpen(!isDropdownOpen)
      inputRef.current?.focus()
    }

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
          <div
            className={classNames(
              styles['multi-select-autocomplete-input-container']
            )}
          >
            <input
              {...(hoveredOptionIndex !== null && {
                'aria-activedescendant': `option-display-${filteredOptions[hoveredOptionIndex]}`,
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
                setHoveredOptionIndex(null)

                onBlur({
                  type: 'blur',
                  target: { name, value: e.target.value },
                })
              }}
            />
            <Toggle
              fieldName={name}
              disabled={disabled}
              isOpen={isDropdownOpen}
              toggleField={toggleDropdown}
            />
          </div>

          {/* Dropdown options list */}
          <div className={styles['field-overlay']}>
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
