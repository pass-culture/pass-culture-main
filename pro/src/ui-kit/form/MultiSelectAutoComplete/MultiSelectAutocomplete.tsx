import React, { useEffect, useRef, useState } from 'react'

import BaseCheckbox from '../shared/BaseCheckbox'
import Icon from 'components/layout/Icon'
import TextInput from '../TextInput'
import cx from 'classnames'
import styles from './MultiSelectAutocomplete.module.scss'
import { useFormikContext } from 'formik'

export type Option = { value: string; label: string }

export interface MultiSelectAutocompleteProps {
  options: Option[]
  onChange?: (
    e:
      | React.ChangeEvent<HTMLInputElement>
      | React.KeyboardEvent<HTMLInputElement>
  ) => void
  label: string
  className?: string
  fieldName: string
  pluralLabel: string
}

const MultiSelectAutocomplete = ({
  options,
  onChange,
  label,
  fieldName,
  className,
  pluralLabel,
}: MultiSelectAutocompleteProps): JSX.Element => {
  const formik = useFormikContext<any>()
  const containerRef = useRef<HTMLDivElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [filteredOptions, setFilteredOptions] = useState(options)
  const {
    values: { [fieldName]: data, [`search-${fieldName}`]: searched },
  } = formik

  useEffect(() => {
    setFilteredOptions(options)
  }, [options])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent): void => {
      if (!containerRef.current?.contains(e.target as Node)) {
        setIsOpen(false)
        formik.setFieldValue(`search-${fieldName}`, '', false)
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
    const regExp = new RegExp(searched === '*' ? /./ : searched, 'i')
    setFilteredOptions(
      options.filter(option => searched === '' || option.label.match(regExp))
    )
  }, [searched])

  return (
    <div
      className={cx(styles['multi-select-autocomplete-container'], className)}
      ref={containerRef}
    >
      <TextInput
        hideFooter
        label={label}
        onFocus={() => {
          if (!isOpen) setIsOpen(true)
        }}
        name={`search-${fieldName}`}
        placeholder={data.length > 1 ? pluralLabel : label}
        style={{ paddingLeft: data.length > 0 ? '2.2rem' : '1rem' }}
      />
      <div className={styles['field-overlay']}>
        <button
          onClick={() => {
            if (isOpen) {
              setIsOpen(false)
              formik.setFieldValue(`search-${fieldName}`, '', false)
            } else {
              setIsOpen(true)
            }
          }}
          className={cx(styles['dropdown-indicator'], {
            [styles['dropdown-indicator-is-closed']]: !isOpen,
          })}
        >
          <Icon
            svg="open-dropdown"
            alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
          />
        </button>
        {data.length > 0 && (
          <div className={styles['pellet']}>{data.length}</div>
        )}
      </div>
      {isOpen && (
        <div className={styles['multi-select-autocomplete__menu']}>
          {filteredOptions.length === 0 && 'Aucun résultat'}
          {filteredOptions.map(({ value, label }) => (
            <BaseCheckbox
              label={label}
              key={`${fieldName}-${value}`}
              value={value}
              name={fieldName}
              onChange={e => {
                formik.handleChange(e)
                onChange?.(e)
              }}
              checked={data.includes(value)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default MultiSelectAutocomplete
