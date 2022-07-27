import React, { useState } from 'react'

import { ReactComponent as CloseButton } from './assets/close.svg'
import { ReactComponent as Banner } from './assets/one_year_banner.svg'
import styles from './BannerOneYear.module.scss'

const BannerOneYear = () => {
  const [isCloseForEver, setIsCloseForEver] = useState(
    localStorage.getItem('iscloseForEver') != null
  )
  const closeForEver = () => {
    localStorage.setItem('iscloseForEver', 'true')
    setIsCloseForEver(localStorage.getItem('iscloseForEver') != null)
  }

  return isCloseForEver ? null : (
    <div className={styles['bannerContainer']}>
      <Banner className={styles['banner']} />
      <CloseButton
        className={styles['closeBanner']}
        onClick={() => closeForEver()}
      />
    </div>
  )
}

export default BannerOneYear
