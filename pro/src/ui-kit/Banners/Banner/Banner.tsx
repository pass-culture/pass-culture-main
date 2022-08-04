import cn from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'

import BannerLayout from '../BannerLayout'
import { IBannerLayoutProps } from '../BannerLayout/BannerLayout'
import styles from '../BannerLayout/BannerLayout.module.scss'

export interface IBannerProps extends IBannerLayoutProps {
  icon?: string
  href?: string
  linkTitle?: string
  children?: React.ReactNode | React.ReactNode[]
  targetLink?: string
  hideLinkIcon?: boolean
}

const Banner = ({
  icon = 'ico-external-site',
  href,
  linkTitle,
  children,
  targetLink = '_blank',
  hideLinkIcon = false,
  ...bannerLayoutProps
}: IBannerProps): JSX.Element => (
  <BannerLayout
    linkNode={
      href &&
      linkTitle && (
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
      )
    }
    {...bannerLayoutProps}
  >
    {children}
  </BannerLayout>
)

export default Banner
