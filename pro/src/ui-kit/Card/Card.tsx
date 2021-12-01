import cn from 'classnames'
import React from 'react'

import HeaderRow from './HeaderRow'
import styles from './Card.module.scss'

type CardStyle = 'primary' | 'secondary'

interface ICardProps {
  children: JSX.Element[] | JSX.Element
  className?: string

  cardStyle?: CardStyle
  secondaryTitle?: string | JSX.Element | null
  title?: string | JSX.Element | null
  titleAction?: JSX.Element[] | JSX.Element | null
  titleIcon?: string | null
}

const Card = ({
  cardStyle = 'primary',
  children,
  className = '',
  secondaryTitle = null,
  title = null,
  titleAction = null,
  titleIcon = null,
}: ICardProps): JSX.Element => {
  const classnames = cn(styles['card'], styles[`card-${cardStyle}`], className)

  return (
    <div className={classnames}>
      <div className={styles['card-inner']}>
        {(title || secondaryTitle) && (
          <HeaderRow
            secondaryTitle={secondaryTitle}
            title={title}
            titleAction={titleAction}
            titleIcon={titleIcon}
          />
        )}
        <div className={styles['card-content']}>
          {secondaryTitle && (
            <h3 className={styles['card-secondary-title']}>{secondaryTitle}</h3>
          )}

          {children}
        </div>
      </div>
    </div>
  )
}

export default Card
