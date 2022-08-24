import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'
import { ReactComponent as CloseIcon } from 'icons/icons-close.svg'

import styles from './BannerLayout.module.scss'

export interface IBannerLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  linkNode?: React.ReactNode | React.ReactNode[]
  type?: 'notification-info' | 'attention' | 'light' | 'new'
  closable?: boolean
  handleOnClick?: () => void
  className?: string
}

const BannerLayout = ({
  children,
  type = 'attention',
  closable = false,
  handleOnClick,
  className,
  linkNode,
}: IBannerLayoutProps): JSX.Element => {
  return (
    <div className={cn(styles['bi-banner'], styles[type], className)}>
      {closable && (
        <button onClick={handleOnClick} type="button">
          <CloseIcon
            title="Masquer le bandeau"
            className={styles['close-icon']}
          />
        </button>
      )}

      <div className={styles['content']}>
        {type === 'new' && (
          <Icon svg="ico-star" className={styles['ico-new']} />
        )}
        <div>
          {children && (
            <span className={styles['bi-banner-text']}>{children}</span>
          )}

          {linkNode}
        </div>
      </div>
    </div>
  )
}

export default BannerLayout
