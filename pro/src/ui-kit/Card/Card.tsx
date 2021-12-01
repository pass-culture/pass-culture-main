import cn from 'classnames'
import React from 'react'

import HeaderRow from './HeaderRow'
import styles from './Card.module.scss'

type CardStyle = 'primary' | 'secondary'

interface ICardProps {
  children: JSX.Element[] | JSX.Element
  className?: string

  cardStyle?: CardStyle,
  title?: string | JSX.Element | null,
  titleAction?: JSX.Element[] | JSX.Element | null,
  titleIcon?: string | null,
  secondaryTitle?: string | JSX.Element | null,
}

const Card = ({
  cardStyle = 'primary',
  children,
  className = '',
  title = null,
  titleAction = null,
  titleIcon = null,
  secondaryTitle = null,
}: ICardProps): JSX.Element => {
  const classnames = cn(styles['card'], styles[`card-${cardStyle}`], className)


  return (
    <div className={classnames}>
      <div className={styles['card-inner']}>
        {(title || secondaryTitle) && (
          <HeaderRow
            title={title}
            titleAction={titleAction}
            titleIcon={titleIcon}
            secondaryTitle={secondaryTitle}
          />
        )}
        <div className={styles['card-content']}>
          { secondaryTitle && (
            <h3 className={styles['card-secondary-title']}>
              {secondaryTitle}
            </h3>
          )}

          { children }
        </div>
      </div>
    </div>
  )
}

export default Card