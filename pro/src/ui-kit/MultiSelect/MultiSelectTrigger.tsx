import { useId, useState } from 'react'

import fullDownIcon from 'icons/full-down.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './MultiSelect.module.scss'

interface MultiSelectTriggerProps {
  className?: string
  isOpen: boolean
  selectedCount: number
  toggleDropdown: () => void
  handleKeyDown: (event: React.KeyboardEvent) => void
  legend: string
  label: string
}

export const MultiSelectTrigger = ({
  className,
  isOpen,
  selectedCount,
  toggleDropdown,
  handleKeyDown,
  legend,
  label,
}: MultiSelectTriggerProps): JSX.Element => {
  const legendId = useId()
  return (
    <>
      <legend id={legendId} className={styles['label']}>
        {legend}
      </legend>
      <button
        type="button"
        className={styles['trigger']}
        onClick={toggleDropdown}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={legendId}
      >
        <div className={styles['trigger-content']}>
          <div className={styles['badge']}>{selectedCount}</div>
          <span>{label}</span>
        </div>
        <SvgIcon
          className={`${styles['chevron']} ${isOpen ? styles['chevronOpen'] : ''}`}
          alt=""
          src={fullDownIcon}
        />
      </button>
    </>
  )
}
