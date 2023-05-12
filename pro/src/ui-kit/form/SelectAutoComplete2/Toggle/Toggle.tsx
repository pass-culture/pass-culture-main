import cx from 'classnames'
import React from 'react'

import Icon from 'ui-kit/Icon/Icon'

import styles from './Toggle.module.scss'

interface ToggleProps {
  disabled: boolean
  isOpen: boolean
  toggleField: () => void
}

const Toggle = ({
  disabled,
  isOpen,
  toggleField,
}: ToggleProps): JSX.Element => {
  return (
    <button
      onClick={toggleField}
      className={cx(styles['dropdown-indicator'], {
        [styles['dropdown-indicator-is-closed']]: !isOpen,
      })}
      type="button"
      disabled={disabled}
    >
      <Icon
        svg="open-dropdown"
        alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
        className={styles['dropdown-indicator-icon']}
      />
    </button>
  )
}

export default Toggle
