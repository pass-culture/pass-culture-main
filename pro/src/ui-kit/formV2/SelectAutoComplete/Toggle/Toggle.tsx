
import strokeDownIcon from 'icons/stroke-down.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Toggle.module.scss'

interface ToggleProps {
  disabled: boolean
  isOpen: boolean
  toggleField: () => void
}

export const Toggle = ({
  disabled,
  isOpen,
  toggleField,
}: ToggleProps): JSX.Element => {
  return (
    <button
      onClick={toggleField}
      className={styles['dropdown-indicator']}
      type="button"
      disabled={disabled}
    >
      <SvgIcon
        src={strokeDownIcon}
        alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
        width="20"
      />
    </button>
  )
}
