import React from 'react'

import styles from './DescriptionList.module.scss'

export interface IListItem {
  label: string
  value: string | null
}

interface IDescriptionListProps {
  list: IListItem[]
}

const DescriptionList = ({list}:IDescriptionListProps) => {
  return (
    <ul className={styles['description-list']}>
      {list.map((listItem:IListItem) => (
        <li>
          <span className={styles['dl-title']}>{listItem.label} :</span>
          <span className={styles['dl-description']}>{listItem.value}</span>
        </li>
      ))}
    </ul>
  )
}

export default DescriptionList
