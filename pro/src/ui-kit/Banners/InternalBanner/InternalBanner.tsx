import type { LocationDescriptor } from 'history'
import React, { FunctionComponent, SVGProps } from 'react'

import { ButtonLink } from 'ui-kit/Button'

import BannerLayout from '../BannerLayout'
import { IBannerLayoutProps } from '../BannerLayout/BannerLayout'
import styles from '../BannerLayout/BannerLayout.module.scss'

interface IInternalBannerProps extends IBannerLayoutProps {
  extraClassName?: string
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  linkTitle: string
  subtitle?: string
  to?: LocationDescriptor
}

const InternalBanner = ({
  extraClassName,
  subtitle,
  children = null,
  to,
  Icon,
  linkTitle,
  ...bannerLayoutProps
}: IInternalBannerProps): JSX.Element => (
  <BannerLayout
    linkNode={
      to ? (
        <ButtonLink
          Icon={Icon}
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
    {children}
  </BannerLayout>
)

export default InternalBanner
