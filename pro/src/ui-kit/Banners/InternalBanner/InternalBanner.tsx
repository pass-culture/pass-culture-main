import type { LocationDescriptor } from 'history'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

import BannerLayout from '../BannerLayout'
import { IBannerLayoutProps } from '../BannerLayout/BannerLayout'
import styles from '../BannerLayout/BannerLayout.module.scss'

interface IInternalBannerProps extends IBannerLayoutProps {
  extraClassName?: string
  icon?: string
  linkTitle: string
  subtitle?: string
  to: LocationDescriptor
}

const InternalBanner = ({
  extraClassName,
  subtitle,
  children = null,
  to,
  icon,
  linkTitle,
  ...bannerLayoutProps
}: IInternalBannerProps): JSX.Element => (
  <BannerLayout
    linkNode={
      <p className={styles['bi-banner-text']}>
        <Link to={to} className={styles['bi-link']}>
          {icon && <Icon svg={icon} />}
          {linkTitle}
        </Link>
      </p>
    }
    className={extraClassName}
    {...bannerLayoutProps}
  >
    <p>{subtitle}</p>
    {children}
  </BannerLayout>
)

export default InternalBanner
