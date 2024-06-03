import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'
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
    <DropdownMenuWrapper title="Opérations sur le stock">
      {actions.map((action, i) => (
        <DropdownItem
          key={`action-${i}`}
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
        </DropdownItem>
      ))}
    </DropdownMenuWrapper>
  )
}
