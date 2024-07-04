import cn from 'classnames'
import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import fullUpIcon from 'icons/full-up.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CellFormatter.module.scss'

export interface DetailsButtonCellProps {
  isExpanded: boolean
  className?: string
}

export const DetailsButtonCell = ({
  isExpanded,
  className,
}: DetailsButtonCellProps) => {
  const { logEvent } = useAnalytics()

  return (
    <div className={cn(className)}>
      <Button
        onClick={() =>
          logEvent(CollectiveBookingsEvents.CLICKED_DETAILS_BUTTON_CELL, {
            from: location.pathname,
          })
        }
        variant={ButtonVariant.TERNARY}
      >
        Détails
        <SvgIcon
          alt=""
          src={fullUpIcon}
          className={cn(styles['details-dropdown-icon'], {
            [styles['details-dropdown-icon-up']]: !isExpanded,
          })}
        />
      </Button>
    </div>
  )
}
