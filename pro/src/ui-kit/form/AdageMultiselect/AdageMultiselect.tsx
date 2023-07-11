import { useCombobox } from 'downshift'
import { useField, useFormikContext } from 'formik'
import React, { useState } from 'react'

import { BaseCheckbox, BaseInput } from '../shared'

import styles from './AdageMultiselect.module.scss'

export interface ItemProps {
  label: string
  value: number
}

interface AdageMultiselectProps {
  options: ItemProps[]
  placeholder: string
  name: string
  label: string
}

const filterAndSortItems = (
  items: ItemProps[],
  selectedItems: ItemProps[],
  inputValue: string
) => {
  const regExp = new RegExp(inputValue, 'i')
  return items
    .filter(item => item.label.match(regExp))
    .sort((a, b) => {
      if (selectedItems.includes(b) && !selectedItems.includes(a)) {
        return 1
      }
      if (!selectedItems.includes(b) && selectedItems.includes(a)) {
        return -1
      }
      return a.label.localeCompare(b.label)
    })
}

const AdageMultiselect = ({
  options,
  placeholder,
  name,
  label,
}: AdageMultiselectProps) => {
  const [inputValue, setInputValue] = useState('')
  const [field] = useField<ItemProps[]>(name)
  const { setFieldValue } = useFormikContext<any>()

  const { getLabelProps, getMenuProps, getInputProps, getItemProps } =
    useCombobox({
      items: filterAndSortItems(options, field.value, inputValue),
      defaultHighlightedIndex: 0, // after selection, highlight the first item.
      selectedItem: null,
      stateReducer(_state, actionAndChanges) {
        const { changes, type } = actionAndChanges
        /* istanbul ignore next: no need to test all case here, downshift behaviour */
        switch (type) {
          case useCombobox.stateChangeTypes.InputKeyDownEnter:
          case useCombobox.stateChangeTypes.ItemClick:
            return {
              ...changes,
              isOpen: true,
              highlightedIndex: 0,
            }
          default:
            return changes
        }
      },
      onInputValueChange: ({ inputValue: newInputValue }) => {
        setInputValue(newInputValue || '')
      },
      itemToString: () => inputValue,
    })

  const handleNewSelection = (selection: ItemProps) => {
    if (field.value.includes(selection)) {
      setFieldValue(
        name,
        field.value.filter(item => item !== selection)
      )
    } else {
      setFieldValue(name, [...field.value, selection])
    }
  }

  return (
    <div className={styles['container']}>
      <label
        htmlFor="search"
        className={styles['search-label']}
        {...getLabelProps()}
      >
        {label}
      </label>
      <BaseInput
        type="search"
        name="search"
        className={styles['search-input']}
        placeholder={placeholder}
        value={inputValue}
        {...getInputProps()}
      />
      <ul className={styles['search-list']} {...getMenuProps()}>
        {filterAndSortItems(options, field.value, inputValue).map(
          (item, index) => {
            // we cannot pass down the ref to basecheckbox as it is a function component
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { ref, ...itemProps } = getItemProps({ item, index })
            return (
              <li key={`${item.value}${index}`}>
                <BaseCheckbox
                  key={`${name}-${item.label}`}
                  label={item.label}
                  name={name}
                  checked={field.value.includes(item)}
                  onChange={() => handleNewSelection(item)}
                  {...itemProps}
                  aria-selected={field.value.includes(item)}
                />
              </li>
            )
          }
        )}
      </ul>
    </div>
  )
}

export default AdageMultiselect
