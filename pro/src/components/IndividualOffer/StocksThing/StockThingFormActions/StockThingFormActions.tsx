import { useMediaQuery } from 'commons/hooks/useMediaQuery'
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
  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

  return (
    <div className={styles['button-actions']}>
      {actions.map((action, i) => (
        <Button
          className={styles['button-action']}
          key={`action-${i}`}
          variant={ButtonVariant.TERNARY}
          icon={action.icon}
          onClick={action.callback}
          tooltipContent={!isMobileScreen ? <>{action.label}</> : undefined}
        />
      ))}
    </div>
  )
}
