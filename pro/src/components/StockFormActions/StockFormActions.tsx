import { Menu, MenuButton, MenuItem, MenuPopover } from '@reach/menu-button'
import { positionRight } from '@reach/popover'
import cn from 'classnames'
import React from 'react'

import fullOtherIcon from 'icons/full-other.svg'
import '@reach/menu-button/styles.css'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StockFormActions.module.scss'
import { StockFormRowAction } from './types'
export interface StockFormActionsProps {
  disabled?: boolean
  actions: StockFormRowAction[]
}
const StockFormActions = ({
  disabled = false,
  actions,
}: StockFormActionsProps): JSX.Element => {
  return (
    <div className={styles['stock-form-actions']}>
      <Menu>
        <MenuButton
          className={styles['menu-button']}
          disabled={disabled}
          title="Opérations sur le stock"
          type="button"
          data-testid="stock-form-actions-button-open"
        >
          <SvgIcon
            src={fullOtherIcon}
            alt="Opérations sur le stock"
            className={styles['menu-button-icon']}
          />
        </MenuButton>

        <MenuPopover position={positionRight} className={styles['menu-list']}>
          {actions.map((action, i) => (
            <MenuItem
              key={`action-${i}`}
              className={cn(styles['menu-item'], {
                [styles['menu-item-disabled']]: action.disabled,
              })}
              disabled={action.disabled}
              onSelect={action.callback}
              title={action.label}
            >
              {action.icon && (
                <SvgIcon
                  src={action.icon}
                  alt=""
                  className={styles['menu-item-icon']}
                />
              )}
              <span>{action.label}</span>
            </MenuItem>
          ))}
        </MenuPopover>
      </Menu>
    </div>
  )
}

export default StockFormActions
