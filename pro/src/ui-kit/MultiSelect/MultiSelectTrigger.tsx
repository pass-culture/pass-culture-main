import cn from 'classnames'

import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './MultiSelect.module.scss'

type MultiSelectTriggerProps = {
  id: string
  isOpen: boolean
  selectedCount: number
  toggleDropdown: () => void
  legend: string
  label: string
  disabled?: boolean
}

export const MultiSelectTrigger = ({
  id,
  isOpen,
  selectedCount,
  toggleDropdown,
  legend,
  label,
  disabled,
}: MultiSelectTriggerProps): JSX.Element => {
  return (
    <>
      <legend className={styles['legend']}>{legend}</legend>
      <button
        type="button"
        className={cn(styles['trigger'], {
          [styles['trigger-selected']]: selectedCount > 0,
        })}
        onClick={toggleDropdown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={id}
        disabled={disabled}
      >
        <div className={styles['trigger-content']}>
          {selectedCount > 0 && (
            <div className={styles['badge']}>
              {selectedCount}{' '}
              <span className={styles['visually-hidden']}>
                éléments sélectionnés
              </span>
            </div>
          )}
          <span className={styles['trigger-label']}>{label}</span>
        </div>
        <SvgIcon
          className={`${styles['chevron']} ${isOpen ? styles['chevronOpen'] : ''}`}
          src={isOpen ? fullUpIcon : fullDownIcon}
        />
      </button>
    </>
  )
}
