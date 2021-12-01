import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'
import styles from './Card.module.scss'


interface IHeaderRowProps {
  titleIcon?: string | null,
  title?: string | JSX.Element | null,
  titleAction?: JSX.Element[] | JSX.Element | null,
  secondaryTitle?: string | JSX.Element | null,
}

const HeaderRow = ({
  titleAction = null,
  title = null,
  secondaryTitle = null,
  titleIcon = null,
}: IHeaderRowProps) => {

  return (
    <div className={styles['card-header-row']}>
      { title && (
        <h3 className={styles['card-title']}>
          { titleIcon && (
            <Icon
              className={styles['card-title-ico']}
              svg={titleIcon}
            />
          )}
          {title}
        </h3>
      )}
      {titleAction && titleAction}
    </div>
  )
}

export default HeaderRow