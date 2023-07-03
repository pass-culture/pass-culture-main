import cn from 'classnames'
import React from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullUpIcon from 'icons/full-up.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CellFormatter.module.scss'

const DetailsButtonCell = ({
  bookingRow,
}: {
  bookingRow: Row<CollectiveBookingResponseModel>
}) => {
  const { logEvent } = useAnalytics()
  return (
    <Button
      onClick={() =>
        logEvent?.(CollectiveBookingsEvents.CLICKED_DETAILS_BUTTON_CELL, {
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
          [styles['details-dropdown-icon-up']]: !bookingRow.isExpanded,
        })}
      />
    </Button>
  )
}

export default DetailsButtonCell
