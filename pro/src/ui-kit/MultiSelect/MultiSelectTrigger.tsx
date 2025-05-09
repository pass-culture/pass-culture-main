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
  buttonLabel: string
  disabled?: boolean
  error?: string
}

export const MultiSelectTrigger = ({
  id,
  isOpen,
  selectedCount,
  toggleDropdown,
  buttonLabel,
  disabled,
  error,
}: MultiSelectTriggerProps): JSX.Element => {
  return (
    <>
      <button
        type="button"
        className={cn(styles['trigger'], {
          [styles['trigger-selected']]: selectedCount > 0,
          [styles['trigger-error']]: !!error,
        })}
        onClick={toggleDropdown}
        aria-haspopup="listbox"
        aria-label={buttonLabel}
        aria-expanded={isOpen}
        aria-controls={id}
        disabled={disabled}
        data-error={!!error}
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
          <span className={styles['trigger-label']}>{buttonLabel}</span>
        </div>
        <SvgIcon
          className={`${styles['chevron']} ${isOpen ? styles['chevronOpen'] : ''} ${disabled ? styles['chevron-disabled'] : ''}`}
          src={isOpen ? fullUpIcon : fullDownIcon}
        />
      </button>
    </>
  )
}
