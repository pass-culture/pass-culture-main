import classNames from 'classnames'

import fullCheckIcon from 'icons/full-check.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import { ToggleButton } from '../ToggleButtonGroup'

import styles from './ToggleButtonGroupButton.module.scss'

interface ToggleButtonGroupButtonProps
  extends React.HTMLProps<HTMLButtonElement> {
  button: ToggleButton
  isActive: boolean
}

export function ToggleButtonGroupButton({
  button,
  isActive,
  ...buttonAttrs
}: ToggleButtonGroupButtonProps) {
  return (
    <div
      className={classNames(styles['button-group-button-container'])}
      key={button.label}
    >
      <Tooltip content={button.label}>
        <button
          className={classNames(styles['button-group-button'], {
            [styles['button-group-button-active']]: isActive,
          })}
          {...buttonAttrs}
          disabled={button.disabled}
          onClick={(e) => button.onClick(button, e)}
          type="button"
          data-testid={`toggle-button${isActive ? '-active' : ''}`}
          aria-label={button.label}
        >
          {isActive && <SvgIcon alt="" src={fullCheckIcon} width="20" />}
          {button.content}
        </button>
      </Tooltip>
    </div>
  )
}
