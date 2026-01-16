import classNames from 'classnames'
import {
  type ForwardedRef,
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import { noop } from '@/commons/utils/noop'
import type { RequiredIndicator } from '@/design-system/common/types'
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
  options: SelectOption[]

  /** Helper text displayed below the input */
  description?: string
  /** Disables the input and prevents interaction */
  disabled?: boolean
  /** Indicates if the field is required */
  required?: boolean
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
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
  /** Called when the search input changes */
  onSearch?(pattern: string): void
  /** Custom function to filter options based on search pattern */
  searchInOptions?(options: SelectOption[], pattern: string): SelectOption[]
  /** Called when the dropdown opens */
  shouldResetOnOpen?: boolean
}

export const SelectAutocomplete = forwardRef(
  (
    {
      className,
      disabled = false,
      name,
      required = true,
      requiredIndicator = 'symbol',
      label,
      options,
      description,
      error,
      onChange = () => noop,
      onBlur = () => noop,
      value,
      onSearch = () => noop,
      searchInOptions = (options, pattern) =>
        options.filter((opt) =>
          opt.label.toLowerCase().includes(pattern.trim().toLowerCase())
        ),
      shouldResetOnOpen = false,
    }: SelectAutocompleteProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const [searchField, setSearchField] = useState('') // Represents the <input type="search"> value while typing (e.g. "Alpes de Ha…")
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
      null
    ) // Represents the index of the hovered option while using keyboard (for a11y), useful for the "aria-activedescendant" attribute

    const optionsLabelByValue = useRef<Map<string, string>>() // Hashtables for the options (ex: "05" -> "Hautes-Alpes")
    const optionsValueByLabel = useRef<Map<string, string>>() // Inverted hashtables for the labels (ex: "Hautes-Alpes" -> "05")
    const containerRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null) // Ref for "searchField"
    const listRef = useRef<HTMLUListElement>(null) // Ref for <ul> dropdown

    useEffect(() => {
      optionsLabelByValue.current = new Map(
        options.map(({ label, value }) => [value as string, label])
      )
      optionsValueByLabel.current = new Map(
        options.map(({ label, value }) => [label, value as string])
      )
    }, [options])

    const handleClickOutside = useCallback((e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        setIsDropdownOpen(false)
      }
    }, [])

    useEffect(() => {
      if (containerRef.current) {
        document.addEventListener('mousedown', handleClickOutside)
      }

      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [handleClickOutside])

    const filteredOptions = searchInOptions(options, searchField)

    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
      switch (event.key) {
        case 'ArrowUp':
          if (hoveredOptionIndex !== null) {
            event.preventDefault()

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

    const selectOption = (option: SelectOption) => {
      setSearchField(option.label)

      onChange({
        type: 'change',
        target: { name, value: option.value },
      })
      onBlur({
        type: 'blur',
        target: { name, value: option.value },
      })

      setIsDropdownOpen(false)
      setHoveredOptionIndex(null)
    }

    const openDropdown = () => {
      if (!isDropdownOpen) {
        setIsDropdownOpen(true)
        if (shouldResetOnOpen) {
          setSearchField('')
          onSearch('')
        }
      }
    }

    const toggleDropdown = () => {
      setIsDropdownOpen(!isDropdownOpen)
      inputRef.current?.focus()
    }

    useEffect(() => {
      const externalValue = value ?? inputRef.current?.value ?? ''

      const externalLabel = optionsLabelByValue.current?.get(externalValue)

      setSearchField(externalLabel || externalValue)
    }, [value])

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <FieldLayout
        className={className}
        error={error}
        required={required}
        requiredIndicator={requiredIndicator}
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
                'aria-activedescendant': `option-${name}-${hoveredOptionIndex}`,
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

                onSearch(e.target.value)

                openDropdown()
              }}
              onBlur={(e) => {
                setSearchField(e.target.value)
                setHoveredOptionIndex(null)

                const value =
                  optionsValueByLabel.current?.get(e.target.value) ?? ''

                onBlur({
                  type: 'blur',
                  target: { name, value },
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

SelectAutocomplete.displayName = 'SelectAutocomplete'
