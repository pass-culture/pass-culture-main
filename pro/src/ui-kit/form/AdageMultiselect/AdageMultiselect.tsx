import { useCombobox } from 'downshift'
import { useField, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { BaseCheckbox, BaseInput } from '../shared'

import styles from './AdageMultiselect.module.scss'

interface ItemProps {
  label: string
  value: number | string | string[]
}

interface AdageMultiselectProps {
  options: ItemProps[]
  placeholder: string
  name: string
  label: string
  isOpen: boolean
}

const filterItems = (items: ItemProps[], inputValue: string) => {
  const regExp = new RegExp(inputValue, 'i')
  return items.filter(item => item.label.match(regExp))
}

const sortItems = (
  items: ItemProps[],
  selectedItems: Set<ItemProps['value']>
) => {
  return items.sort((a, b) => {
    if (selectedItems.has(b.value) && !selectedItems.has(a.value)) {
      return 1
    }
    if (!selectedItems.has(b.value) && selectedItems.has(a.value)) {
      return -1
    }
    return a.label.localeCompare(b.label)
  })
}

const isIncluded = (
  fieldValue: ItemProps['value'][],
  value: ItemProps['value']
): boolean => {
  if (Array.isArray(value)) {
    const valueSet = new Set(value)
    return fieldValue.some(
      fieldValueItem =>
        Array.isArray(fieldValueItem) &&
        fieldValueItem.length === value.length &&
        fieldValueItem.every(val => valueSet.has(val))
    )
  }

  return fieldValue.includes(value)
}

const AdageMultiselect = ({
  options,
  placeholder,
  name,
  label,
  isOpen,
}: AdageMultiselectProps) => {
  const [inputValue, setInputValue] = useState('')
  const [field] = useField<ItemProps['value'][]>(name)
  const { setFieldValue } = useFormikContext<any>()
  const [sortedOptions, setSortedOptions] = useState<ItemProps[]>([])
  useEffect(() => {
    setSortedOptions(sortItems(options, new Set(field.value)))
  }, [isOpen])

  const { getLabelProps, getMenuProps, getInputProps, getItemProps } =
    useCombobox({
      items: sortedOptions,
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
    if (isIncluded(field.value, selection.value)) {
      setFieldValue(
        name,
        field.value.filter(item => item !== selection.value)
      )
    } else {
      setFieldValue(name, [...field.value, selection.value])
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
      <ul
        className={styles['search-list']}
        {...getMenuProps({
          'aria-activedescendant': getInputProps()['aria-activedescendant'],
        })}
      >
        {filterItems(options, inputValue).map((item, index) => {
          // we cannot pass down the ref to basecheckbox as it is a function component
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          const { ref, ...itemProps } = getItemProps({ item, index })
          const liValueKey = Array.isArray(item.value)
            ? item.value.join('_')
            : item.value

          const isChecked = isIncluded(field.value, item.value)

          return (
            <li key={`${liValueKey}`}>
              <BaseCheckbox
                key={`${name}-${item.label}`}
                label={item.label}
                name={name}
                checked={isChecked}
                onChange={() => handleNewSelection(item)}
                {...itemProps}
                aria-selected={isChecked}
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export default AdageMultiselect
