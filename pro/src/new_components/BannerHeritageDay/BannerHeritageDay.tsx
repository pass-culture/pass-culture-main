import React, { useState } from 'react'

import { ReactComponent as CloseButton } from './assets/close.svg'
import { ReactComponent as Banner } from './assets/heritage_day_banner.svg'
import styles from './BannerHeritageDay.module.scss'

const BannerHeritageDay = () => {
  const [isOpenBanner, setIsOpenBanner] = useState(true)
  const closeBanner = () => {
    setIsOpenBanner(false)
  }

  return isOpenBanner ? (
    <div className={styles['bannerContainer']}>
      <a href="https://docsend.com/view/eqbmkrz38ea3i557" target="_blank">
        <Banner className={styles['banner']} />
      </a>
      <CloseButton
        className={styles['openBanner']}
        onClick={() => closeBanner()}
      />
    </div>
  ) : null
}

export default BannerHeritageDay
