import React from 'react'

import styles from './CellFormatter.module.scss'

interface BookingIdCellProps {
  id: string
}

export const BookingIdCell = ({ id }: BookingIdCellProps) => {
  return <div className={styles['booking-id']}>{id}</div>
}
