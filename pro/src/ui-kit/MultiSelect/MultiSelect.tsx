import { useEffect, useRef, useState } from 'react'
import { SelectedValuesTags } from 'ui-kit/form/SelectAutoComplete/SelectedValuesTags/SelectedValuesTags'

import styles from './MultiSelect.module.scss'
import { MultiSelectPanel } from './MultiSelectPanel'
import { MultiSelectTrigger } from './MultiSelectTrigger'

export type Option = {
  id: string
  label: string
}

type MultiSelectProps = {
  options: Option[]
  defaultOptions?: Option[]
  label: string
  legend: string
  hasSearch?: boolean
  searchExample?: string
  searchLabel?: string
  hasSelectAllOptions?: boolean
  disabled?: boolean
}

export const MultiSelect = ({
  options,
  defaultOptions,
  hasSearch,
  searchExample,
  searchLabel,
  label,
  legend,
  hasSelectAllOptions,
  disabled,
}: MultiSelectProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLFieldSetElement>(null)
  const [selectedItems, setSelectedItems] = useState<Option[]>(
    defaultOptions ?? []
  )

  const handleSelectOrRemoveItem = (item: Option | 'all' | undefined) => {
    if (item === 'all') {
      setSelectedItems(options)
    } else if (item === undefined) {
      setSelectedItems([])
    } else {
      setSelectedItems((prev) =>
        prev.some((prevItem) => prevItem.id === item.id)
          ? prev.filter((prevItem) => prevItem.id !== item.id)
          : [...prev, item]
      )
    }
  }

  const handleRemoveItem = (itemId: string) => {
    setSelectedItems((prev) => prev.filter((item) => item.id !== itemId))
  }

  const toggleDropdown = () => setIsOpen(!isOpen)

  const handleKeyDown = (event: React.KeyboardEvent) => {
    event.preventDefault()
    if (event.key === 'Enter' || event.key === ' ') {
      toggleDropdown()
    }
  }

  useEffect(() => {
    const handleWindowClick = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    window.addEventListener('click', handleWindowClick)
    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('click', handleWindowClick)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  return (
    <fieldset
      className={styles['container']}
      style={{ position: 'relative' }}
      ref={containerRef}
    >
      <MultiSelectTrigger
        legend={legend}
        label={label}
        isOpen={isOpen}
        toggleDropdown={toggleDropdown}
        handleKeyDown={handleKeyDown}
        selectedCount={selectedItems.length}
        disabled={disabled}
      />

      {isOpen && (
        <MultiSelectPanel
          label={label}
          options={options.map((option) => ({
            ...option,
            checked: selectedItems.some((item) => item.id === option.id),
          }))}
          onOptionSelect={handleSelectOrRemoveItem}
          hasSearch={hasSearch}
          searchExample={searchExample}
          searchLabel={searchLabel}
          hasSelectAllOptions={hasSelectAllOptions}
        />
      )}

      <SelectedValuesTags
        disabled={disabled}
        selectedOptions={selectedItems.map((item) => item.id)}
        removeOption={handleRemoveItem}
        fieldName="tags"
        optionsLabelById={selectedItems.reduce(
          (acc, item) => ({ ...acc, [item.id]: item.label }),
          {}
        )}
      />
    </fieldset>
  )
}

{
  /* <fieldset>
	<legend><button aria-controls="control-id" aria-expanded=...>Label du bouton</button></legend>
	<div id="control-id">
		<label class="visually-hidden" for="id-input">Rechercher des ...</label>
		<svg> // icon visuelle
		<input type="search" id="id-input"/>
		<ul>
			<li><input /> <label>...</label></li>
			<li></li>
			<li></li>
		</ul>
	</div>
</fieldset>
<div
  role="listbox"
  tabindex="0"
  id="listbox1"
  onclick="return listItemClick(event);"
  onkeydown="return listItemKeyEvent(event);"
  onkeypress="return listItemKeyEvent(event);"
  onfocus="this.className='focus';"
  onblur="this.className='blur';"
  aria-activedescendant="listbox1-1">
  <div role="option" id="listbox1-1" class="selected">Vert</div>
  <div role="option" id="listbox1-2">Orange</div>
  <div role="option" id="listbox1-3">Rouge</div>
  <div role="option" id="listbox1-4">Bleu</div>
  <div role="option" id="listbox1-5">Violet</div>
  <div role="option" id="listbox1-6">Pervenche</div>
</div>
*/
}

{
  /* <div className={styles.container} role="listbox" aria-label="Liste des départements">
      {departments.map(department => (
        <label key={department.id} className={styles.item}>
          <div className={styles.checkbox}>
            <input
              type="checkbox"
              checked={department.checked}
              onChange={() => handleCheckboxChange(department.id)}
              className={styles.input}
            />
            <span className={styles.checkmark} aria-hidden="true" />
          </div>
          <span className={styles.label}>{department.name}</span>
        </label>
      ))}
    </div> */
}
