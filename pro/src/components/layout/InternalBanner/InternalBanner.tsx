import cn from 'classnames'
import React from 'react'

import { Banner } from 'ui-kit'

import styles from './InternalBanner.module.scss'

interface IInternalBannerProps {
  children?: string | null
  extraClassName?: string
  href: string
  icon?: string
  linkTitle: string
  subtitle?: string
  type?: 'notification-info' | 'attention'
}

const InternalBanner = ({
  children = null,
  extraClassName = '',
  href,
  icon,
  linkTitle,
  subtitle = '',
  type = 'attention',
}: IInternalBannerProps): JSX.Element => (
  <Banner
    className={cn(styles['internal-banner'], extraClassName)}
    href={href}
    linkTitle={linkTitle}
    hideLinkIcon={!icon}
    icon={icon}
    type={type}
  >
    <>{subtitle}</>

    {children && <>{children}</>}
  </Banner>
)

export default InternalBanner
