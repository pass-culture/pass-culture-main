import { useMediaQuery } from 'hooks/useMediaQuery'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './StockThingFormActions.module.scss'
import { StockFormRowAction } from './types'

export interface StockThingFormActionsProps {
  actions: StockFormRowAction[]
}

export const StockThingFormActions = ({
  actions,
}: StockThingFormActionsProps): JSX.Element => {
  const isMobileScreen = useMediaQuery('(max-width: 46.5rem)')

  return (
    <div className={styles['button-actions']}>
      {actions.map((action, i) => (
        <Button
          className={styles['button-action']}
          key={`action-${i}`}
          variant={ButtonVariant.TERNARY}
          icon={action.icon}
          onClick={action.callback}
          hasTooltip={!isMobileScreen}
        >
          {action.label}
        </Button>
      ))}
    </div>
  )
}
