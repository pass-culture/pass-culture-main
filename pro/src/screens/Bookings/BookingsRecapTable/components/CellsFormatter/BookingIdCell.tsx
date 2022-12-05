import React from 'react'

import styles from './CellFormatter.module.scss'

const BookingIdCell = ({ id }: { id: string }) => {
  return <div className={styles['booking-id']}>{id}</div>
}

export default BookingIdCell
