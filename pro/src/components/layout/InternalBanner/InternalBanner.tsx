import Icon from 'components/layout/Icon'
import React from 'react'
import cn from 'classnames'
import styles from './InternalBanner.module.scss'

interface IInternalBannerProps {
  children?: string | null
  extraClassName?: string
  href: string
  icon?: string | null
  linkTitle: string
  subtitle?: string
  type?: 'notification-info' | 'attention'
}

const InternalBanner = ({
  children = null,
  extraClassName = '',
  href,
  icon = null,
  linkTitle,
  subtitle = '',
  type = 'attention',
}: IInternalBannerProps): JSX.Element => (
  <div
    className={cn(styles['internal-banner'], 'bi-banner', type, extraClassName)}
  >
    <p>{subtitle}</p>

    {children && <p>{children}</p>}

    <p>
      <a
        className={cn(styles['internal-link'], 'bi-link', 'tertiary-link')}
        href={href}
      >
        {icon && <Icon svg={icon} />}
        {linkTitle}
      </a>
    </p>
  </div>
)

export default InternalBanner
