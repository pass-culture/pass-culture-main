import cn from 'classnames'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'

interface DetailsButtonCellProps {
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
  return (
    <div className={cn(className)}>
      <Button
        onClick={onClick}
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={isExpanded ? fullUpIcon : fullDownIcon}
        iconPosition={IconPositionEnum.RIGHT}
        aria-expanded={isExpanded}
        aria-controls={controlledId}
        label="Détails"
      />
    </div>
  )
}
