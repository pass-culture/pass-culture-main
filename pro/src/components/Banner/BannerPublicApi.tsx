import cn from 'classnames'
import React from 'react'

import { LogoPassCultureDarkIcon } from 'icons'
import Banner from 'ui-kit/Banners/Banner'

import styles from './BannerPublicApi.module.scss'

interface Props {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const BannerPublicApi = ({ children, className }: Props): JSX.Element => (
  <Banner showTitle={false} type="notification-info" className={cn(className)}>
    <div className={styles['banner-container']}>
      <LogoPassCultureDarkIcon className={styles['banner-logo']} />
      {children}
    </div>
  </Banner>
)

export default BannerPublicApi
