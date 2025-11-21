import type React from 'react'

import { Banner } from '@/design-system/Banner/Banner'
import logoPassCultureIcon from '@/icons/logo-pass-culture.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BannerPublicApi.module.scss'

interface Props {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

export const BannerPublicApi = ({
  children,
  className,
}: Props): JSX.Element => (
  <div className={className}>
    <Banner
      title=""
      description={
        <div className={styles['banner-container']}>
          <SvgIcon
            src={logoPassCultureIcon}
            alt=""
            className={styles['banner-logo']}
            viewBox="0 0 71 24"
          />
          {children}
        </div>
      }
    />
  </div>
)
