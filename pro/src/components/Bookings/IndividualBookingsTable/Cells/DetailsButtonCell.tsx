import cn from 'classnames'

import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'

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
