import React from 'react'

import styles from './DataDisplaying.module.scss'

type DataDisplayingLines = {
  lines: {
    label: string
    value: string | JSX.Element[]
  }[]
}

export const DataDisplaying = ({ lines }: DataDisplayingLines): JSX.Element => {
  return (
    <dl className={styles['data-displaying']}>
      {lines.map(({ label, value }) => (
        <React.Fragment key={label}>
          <dt className={styles['data-term']}>{label}</dt>
          <dd className={styles['data-definition']}>{value}</dd>
        </React.Fragment>
      ))}
    </dl>
  )
}
