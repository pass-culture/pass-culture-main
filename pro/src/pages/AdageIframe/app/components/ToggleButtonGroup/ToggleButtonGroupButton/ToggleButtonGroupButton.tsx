import classNames from 'classnames'

import fullCheck from 'icons/full-check.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

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
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)

  return (
    <div
      className={classNames(styles['button-group-button-container'])}
      key={button.label}
    >
      <button
        className={classNames(styles['button-group-button'], {
          [styles['button-group-button-active']]: isActive,
        })}
        {...tooltipProps}
        {...buttonAttrs}
        disabled={button.disabled}
        onClick={(e) => button.onClick(button, e)}
        type="button"
        data-testid={`toggle-button${isActive ? '-active' : ''}`}
        aria-label={button.label}
      >
        {isActive && <SvgIcon alt="" src={fullCheck} width="20" />}
        <Tooltip content={button.label} visuallyHidden={isTooltipHidden}>
          {button.content}
        </Tooltip>
      </button>
    </div>
  )
}
