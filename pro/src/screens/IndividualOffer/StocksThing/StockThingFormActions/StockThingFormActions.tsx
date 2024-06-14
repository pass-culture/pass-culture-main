import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StockThingFormActions.module.scss'
import { StockFormRowAction } from './types'

export interface StockThingFormActionsProps {
  actions: StockFormRowAction[]
}

export const StockThingFormActions = ({
  actions,
}: StockThingFormActionsProps): JSX.Element => {
  return (
    <>
      <DropdownMenuWrapper
        title="Opérations sur le stock"
        className={styles['dropdown-actions']}
      >
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

      {/* We only display this buttons on small screen */}
      <div className={styles['button-actions']}>
        {actions.map((action, i) => (
          <Button
            className={styles['button-action']}
            key={`action-${i}`}
            variant={ButtonVariant.TERNARY}
            icon={action.icon}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </>
  )
}
