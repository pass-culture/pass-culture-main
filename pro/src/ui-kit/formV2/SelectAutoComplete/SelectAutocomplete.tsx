import cx from 'classnames'
import {
  ForwardedRef,
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'

import { SelectOption } from 'commons/custom_types/form'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import { OptionsList } from './OptionsList/OptionsList'
import styles from './SelectAutocomplete.module.scss'
import { Toggle } from './Toggle/Toggle'

type CustomEvent<T extends 'change' | 'blur'> = {
  type: T
  target: { name: string; value: string }
}

type CommonProps = {
  name: string
  label: string | JSX.Element
  options: SelectOption[]

  description?: string
  disabled?: boolean
  isOptional?: boolean
  className?: string
  error?: string
  hideArrow?: boolean
  onChange?(e: CustomEvent<'change'>): void
  onBlur?(e: CustomEvent<'blur'>): void
  onSearch?(pattern: string): void
  searchInOptions?(options: SelectOption[], pattern: string): SelectOption[]
}
type WithResetOnOpen = {
  resetOnOpen?: true
  onReset?(): void
}
type WithoutResetOnOpen = {
  resetOnOpen?: false
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
      isOptional = false,
      label,
      options,
      resetOnOpen = true,
      description,
      error,
      onChange = () => {},
      onBlur = () => {},
      onSearch = () => {},
      searchInOptions = (options, pattern) =>
        options.filter((opt) =>
          opt.label.toLowerCase().includes(pattern.trim().toLowerCase())
        ),
      onReset = () => {},
    }: SelectAutocompleteProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const [searchField, setSearchField] = useState('') // Represents the <input type="search"> value while typing (e.g. "Alpes de Ha…")
    const [field, setField] = useState('') // Represents the actual selected <option>’s "value" attribute among the options (e.g. "04")
    const [isOpen, setIsOpen] = useState(false) // Represents the state of the dropdown options list
    const [hoveredOptionIndex, setHoveredOptionIndex] = useState<number | null>(
      null
    ) // Represents the index of the hovered option while using keyboard (for a11y), useful for the "aria-activedescendant" attribute

    const optionsLabelById = useRef<Map<string, string>>() // Hashtables for the options (ex: "05" -> "Hautes-Alpes")
    const optionsIdByLabel = useRef<Map<string, string>>() // Inverted hashtables for the labels (ex: "Hautes-Alpes" -> "05")
    const hasComponentFirstRendered = useRef(false)
    const containerRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null) // Ref for "searchField"
    const listRef = useRef<HTMLUListElement>(null) // Ref for <ul> dropdown
    const selectRef = useRef<HTMLSelectElement>(null) // Ref for hidden <select> (a11y)

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
      if (resetOnOpen && isOpen && searchField !== '') {
        setField('')
        setSearchField('')
        onReset()
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isOpen, resetOnOpen])

    // Clicking outside the container will close the dropdown
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
              selectOption(String(filteredOptions[hoveredOptionIndex].value))
            }
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
          break
      }
    }

    // When an option is chosen
    const selectOption = (value: string) => {
      // Update selected value and search text internally
      setField(value)
      setSearchField(optionsLabelById.current?.get(value) ?? '')

      // Then notify changes up to the parent component
      onChange({ type: 'change', target: { name, value } })
      onBlur({ type: 'blur', target: { name, value } })

      // Close dropdown and reset hovered index (a11y)
      setIsOpen(false)
      setHoveredOptionIndex(null)
    }

    // Dropdown open
    const open = () => {
      if (!isOpen) {
        setIsOpen(true)
      }
    }

    // Dropdown toggle
    const toggle = () => {
      if (!isOpen) {
        setIsOpen(true)
      } else {
        setIsOpen(false)
        setSearchField('')
      }
    }

    // When the inputRef’s value changes externally, associate the new value to the good label in the "searchField" (ex: "05" -> "Hautes-Alpes")
    useEffect(() => {
      setSearchField(
        optionsLabelById.current?.get(inputRef.current?.value ?? '') ?? ''
      )
      setField(inputRef.current?.value ?? '') // Provokes a re-render and also updates the hidden <select> element connected to the "field" (a11y)
    }, [inputRef])

    // Connect the external reference to the internal one "inputRef", so we can read it's value in the "useEffect" above
    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    return (
      <FieldLayout
        className={className}
        error={error}
        isOptional={isOptional}
        label={label}
        name={name}
        showError={!!error}
        description={description}
      >
        <div
          className={cx(
            styles['multi-select-autocomplete-container'],
            className
          )}
          onKeyDown={handleKeyDown}
          ref={containerRef}
        >
          {/* Search field */}
          <BaseInput
            {...(hoveredOptionIndex !== null && {
              'aria-activedescendant': `option-display-${filteredOptions[hoveredOptionIndex]?.value}`,
            })}
            onClick={open}
            onFocus={open}
            className={styles['multi-select-autocomplete-placeholder-input']}
            hasError={!!error}
            type="search"
            disabled={disabled}
            aria-autocomplete="list"
            aria-controls={`list-${name}`}
            aria-describedby={`help-${name}`}
            aria-expanded={isOpen}
            aria-haspopup="listbox"
            aria-required={!isOptional}
            role="combobox"
            value={searchField}
            autoComplete="off"
            ref={inputRef}
            name={name}
            onChange={(e) => setSearchField(e.target.value)}
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

          {/* START : Accessibility for voice synthesis */}
          <div
            aria-live="polite"
            aria-relevant="text"
            className={styles['visually-hidden']}
            id={`help-${name}`}
          >
            {field !== '' &&
              `Option sélectionnée : ${optionsLabelById.current?.get(field) ?? ''}. `}
            {isOpen
              ? `${filteredOptions.length} options ${
                  searchField === ''
                    ? 'disponibles. '
                    : 'correspondant au texte saisi. '
                }`
              : 'Saisissez du texte pour afficher et filtrer les options.'}
          </div>
          <select
            hidden
            ref={selectRef}
            value={field || ''}
            onChange={() => {}} // Silent React warning that is irrelevant here
            data-testid="select"
          >
            {options.map(({ label, value }) => (
              <option key={`option-${value}`} value={value}>
                {label}
              </option>
            ))}
          </select>
          {/* END : Accessibility for voice synthesis */}

          {/* Dropdown options list */}
          <div className={styles['field-overlay']}>
            {!hideArrow && (
              <Toggle
                disabled={disabled}
                isOpen={isOpen}
                toggleField={toggle}
              />
            )}
            {isOpen && (
              <OptionsList
                className={className}
                fieldName={name}
                selectedValues={field}
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
