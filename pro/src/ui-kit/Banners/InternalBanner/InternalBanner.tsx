import React from 'react'

import { ButtonLink } from 'ui-kit/Button'

import BannerLayout from '../BannerLayout'
import { BannerLayoutProps } from '../BannerLayout/BannerLayout'
import styles from '../BannerLayout/BannerLayout.module.scss'

interface InternalBannerProps extends BannerLayoutProps {
  extraClassName?: string
  icon?: string
  linkTitle: string
  subtitle?: string
  to?: string
}

const InternalBanner = ({
  extraClassName,
  subtitle,
  to,
  icon,
  linkTitle,
  ...bannerLayoutProps
}: InternalBannerProps): JSX.Element => (
  <BannerLayout
    linkNode={
      to ? (
        <ButtonLink
          icon={icon}
          link={{ isExternal: false, to }}
          className={styles['bi-link']}
        >
          {linkTitle}
        </ButtonLink>
      ) : undefined
    }
    className={extraClassName}
    {...bannerLayoutProps}
  >
    <p>{subtitle}</p>
    {bannerLayoutProps.children}
  </BannerLayout>
)

export default InternalBanner
