import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './Banner.module.scss'

export interface IBannerProps {
  icon?: string
  href?: string
  linkTitle?: string
  children?: React.ReactNode | React.ReactNode[]
  targetLink?: string
  type?: 'notification-info' | 'attention' | 'light'
  closable?: boolean
  handleOnClick?: () => void
  className?: string
  hideLinkIcon?: boolean
}

const Banner = ({
  icon = 'ico-external-site',
  href,
  linkTitle,
  children,
  targetLink = '_blank',
  type = 'attention',
  closable = false,
  handleOnClick,
  className,
  hideLinkIcon = false,
}: IBannerProps): JSX.Element => {
  return (
    <div className={cn(styles['bi-banner'], styles[type], className)}>
      {closable && (
        <button onClick={handleOnClick} type="button">
          <Icon alt="Masquer le bandeau" svg="icons-close" />
        </button>
      )}

      {children && <p className={styles['bi-banner-text']}>{children}</p>}

      {href && linkTitle && (
        <p className={styles['bi-banner-text']}>
          <a
            className={cn(styles['bi-link'])}
            href={href}
            rel="noopener noreferrer"
            target={targetLink}
          >
            {!hideLinkIcon && <Icon svg={icon} />}
            {linkTitle}
          </a>
        </p>
      )}
    </div>
  )
}

export default Banner
