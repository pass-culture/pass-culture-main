import { Menu, MenuButton, MenuItem, MenuPopover } from '@reach/menu-button'
import { positionRight } from '@reach/popover'
import cn from 'classnames'
import React from 'react'

import { ReactComponent as OptionMenuIcon } from 'icons/ico-more-horiz.svg'

import styles from './StockFormActions.module.scss'
import { IStockFormRowAction } from './types'

export interface IStockFormActionsProps {
  disabled?: boolean
  actions: IStockFormRowAction[]
}
const StockFormActions = ({
  disabled = false,
  actions,
}: IStockFormActionsProps): JSX.Element => {
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
          <OptionMenuIcon
            title="Opérations sur le stock"
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
              {action.Icon && (
                <action.Icon
                  title={action.label}
                  aria-hidden
                  className={styles['menu-item-icon']}
                />
              )}
              <span className={styles['menu-item-text']}>{action.label}</span>
            </MenuItem>
          ))}
        </MenuPopover>
      </Menu>
    </div>
  )
}

export default StockFormActions
