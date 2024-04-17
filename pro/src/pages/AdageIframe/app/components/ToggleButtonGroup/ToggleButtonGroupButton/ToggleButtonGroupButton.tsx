import classNames from 'classnames'

import fullCheck from 'icons/full-check.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import { ToggleButton } from '../ToggleButtonGroup'

import styles from './ToggleButtonGroupButton.module.scss'

interface ToggleButtonGroupButtonProps
  extends React.HTMLProps<HTMLButtonElement> {
  button: ToggleButton
  isActive: boolean
}

export default function ToggleButtonGroupButton({
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
      <Tooltip content={button.label} visuallyHidden={isTooltipHidden}>
        <button
          className={classNames(styles['button-group-button'], {
            [styles['button-group-button-active']]: isActive,
          })}
          {...tooltipProps}
          {...buttonAttrs}
          disabled={button.disabled}
          onClick={(e) => button.onClick(button, e)}
          type="button"
        >
          {isActive && <SvgIcon alt="" src={fullCheck} width="20" />}
          {button.content}
        </button>
      </Tooltip>
    </div>
  )
}
