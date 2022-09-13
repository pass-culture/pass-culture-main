import cn from 'classnames'
import React from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { ReactComponent as DropdownIcon } from 'icons/ico-arrow-up-b.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CellFormatter.module.scss'

const DetailsButtonCell = ({
  bookingRow,
}: {
  bookingRow: Row<CollectiveBookingResponseModel>
}) => {
  return (
    <Button
      variant={ButtonVariant.TERNARY}
      {...bookingRow.getToggleRowExpandedProps()}
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
