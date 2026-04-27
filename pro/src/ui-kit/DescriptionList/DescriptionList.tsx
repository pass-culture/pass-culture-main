import React from 'react'

import styles from './DescriptionList.module.scss'

type DescriptionListData = {
  lines: {
    label: string
    value: string | JSX.Element | (string | JSX.Element)[]
  }[]
}

export const DescriptionList = ({
  lines,
}: DescriptionListData): JSX.Element => {
  return (
    <dl className={styles['description-list']}>
      {lines.map(({ label, value }) => (
        <React.Fragment key={label}>
          <dt className={styles['data-term']}>{label}</dt>
          {Array.isArray(value) ? (
            value.map((definition) => (
              <dd
                className={styles['data-definition']}
                key={
                  typeof definition === 'string' ? definition : definition.key
                }
              >
                {definition}
              </dd>
            ))
          ) : (
            <dd className={styles['data-definition']}>{value}</dd>
          )}
        </React.Fragment>
      ))}
    </dl>
  )
}
