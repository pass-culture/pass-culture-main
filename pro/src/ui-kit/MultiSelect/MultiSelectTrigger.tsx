import cn from 'classnames'
import { useId } from 'react'

import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './MultiSelect.module.scss'

type MultiSelectTriggerProps = {
  isOpen: boolean
  selectedCount: number
  toggleDropdown: () => void
  handleKeyDown: (event: React.KeyboardEvent) => void
  legend: string
  label: string
  disabled?: boolean
}

export const MultiSelectTrigger = ({
  isOpen,
  selectedCount,
  toggleDropdown,
  handleKeyDown,
  legend,
  label,
  disabled,
}: MultiSelectTriggerProps): JSX.Element => {
  const legendId = useId()
  return (
    <>
      <legend id={legendId} className={styles['legend']}>
        {legend}
      </legend>
      <button
        type="button"
        className={cn(styles['trigger'], {
          [styles['trigger-selected']]: selectedCount > 0,
        })}
        onClick={toggleDropdown}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={legendId}
        disabled={disabled}
      >
        <div className={styles['trigger-content']}>
          {selectedCount > 0 && (
            <div className={styles['badge']}>{selectedCount}</div>
          )}
          <span className={styles['trigger-label']}>{label}</span>
        </div>
        <SvgIcon
          className={`${styles['chevron']} ${isOpen ? styles['chevronOpen'] : ''}`}
          alt=""
          src={isOpen ? fullUpIcon : fullDownIcon}
        />
      </button>
    </>
  )
}
