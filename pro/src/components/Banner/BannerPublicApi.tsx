import cn from 'classnames'
import React from 'react'

import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import Banner from 'ui-kit/Banners/Banner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BannerPublicApi.module.scss'

interface Props {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const BannerPublicApi = ({ children, className }: Props): JSX.Element => (
  <Banner showTitle={false} type="notification-info" className={cn(className)}>
    <div className={styles['banner-container']}>
      <SvgIcon
        src={logoPassCultureIcon}
        alt=""
        className={styles['banner-logo']}
        viewBox="0 0 71 24"
      />
      {children}
    </div>
  </Banner>
)

export default BannerPublicApi
