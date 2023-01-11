import cn from 'classnames'
import React from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as DropdownIcon } from 'icons/ico-arrow-up-b.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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
        logEvent?.(Events.CLICKED_DETAILS_BUTTON_CELL, {
          from: location.pathname,
        })
      }
      variant={ButtonVariant.TERNARY}
    >
      Détails
      <DropdownIcon
        className={cn(styles['details-dropdown-icon'], {
          [styles['details-dropdown-icon-up']]: !bookingRow.isExpanded,
        })}
      />
    </Button>
  )
}

export default DetailsButtonCell
