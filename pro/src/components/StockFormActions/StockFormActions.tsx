import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'

import fullOtherIcon from 'icons/full-other.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StockFormActions.module.scss'
import { StockFormRowAction } from './types'

export interface StockFormActionsProps {
  actions: StockFormRowAction[]
}

export const StockFormActions = ({
  actions,
}: StockFormActionsProps): JSX.Element => {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={styles['menu-button']}
        title="Opérations sur le stock"
        data-testid="stock-form-actions-button-open"
      >
        <SvgIcon
          src={fullOtherIcon}
          alt="Opérations sur le stock"
          className={styles['menu-button-icon']}
        />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content className={styles['menu-list']} align="end">
          {actions.map((action, i) => (
            <DropdownMenu.Item
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
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
