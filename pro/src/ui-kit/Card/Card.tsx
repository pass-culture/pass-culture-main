import type { ReactNode } from 'react'

import styles from './Card.module.scss'

type CardProps = {
  imageSrc: string
  title: ReactNode
  children: ReactNode
  actions: ReactNode
}

export const Card = ({ imageSrc, title, children, actions }: CardProps) => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <div>
          <img src={imageSrc} alt="" className={styles['card-image']} />
          {title}
          <p className={styles['card-description']}>{children}</p>
        </div>
        <div className={styles['card-button']}>{actions}</div>
      </div>
    </div>
  )
}
