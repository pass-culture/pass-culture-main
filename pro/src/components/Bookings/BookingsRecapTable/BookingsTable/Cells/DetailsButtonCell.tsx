import cn from 'classnames'

import { useAnalytics } from 'app/App/analytics/firebase'
import { CollectiveBookingsEvents } from 'commons/core/FirebaseEvents/constants'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface DetailsButtonCellProps {
  controlledId: string
  isExpanded: boolean
  className?: string
  onClick: () => void
}

export const DetailsButtonCell = ({
  controlledId,
  isExpanded,
  className,
  onClick,
}: DetailsButtonCellProps) => {
  const { logEvent } = useAnalytics()

  return (
    <div className={cn(className)}>
      <Button
        onClick={() => {
          onClick()
          logEvent(CollectiveBookingsEvents.CLICKED_DETAILS_BUTTON_CELL, {
            from: location.pathname,
          })
        }}
        variant={ButtonVariant.TERNARY}
        icon={isExpanded ? fullUpIcon : fullDownIcon}
        iconPosition={IconPositionEnum.RIGHT}
        aria-expanded={isExpanded}
        aria-controls={controlledId}
      >
        Détails
      </Button>
    </div>
  )
}
