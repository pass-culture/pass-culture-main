import cx from 'classnames'

import fullDownIcon from '@/icons/full-down.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Toggle.module.scss'

export interface ToggleProps {
  fieldName: string
  disabled: boolean
  isOpen: boolean
  toggleField: () => void
}

export const Toggle = ({
  fieldName,
  disabled,
  isOpen,
  toggleField,
}: ToggleProps): JSX.Element => {
  return (
    <button
      onClick={toggleField}
      className={styles['dropdown-indicator']}
      type="button"
      aria-expanded={isOpen}
      aria-label={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
      aria-controls={`list-${fieldName}`}
      disabled={disabled}
      tabIndex={-1}
    >
      <SvgIcon
        className={cx({ [styles['dropdown-indicator--open']]: isOpen })}
        src={fullDownIcon}
      />
    </button>
  )
}
