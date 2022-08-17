import React from 'react'

import { ReactComponent as CloseButton } from './assets/close.svg'
import { ReactComponent as Banner } from './assets/heritage_day_banner.svg'
import styles from './BannerHeritageDay.module.scss'

export interface IBannerHeritageDayProps {
  setIsBannerHeritageDayVisible: (b: boolean) => void
  isBannerHeritageDayVisible: boolean
}
const BannerHeritageDay = ({
  isBannerHeritageDayVisible,
  setIsBannerHeritageDayVisible,
}: IBannerHeritageDayProps) => {
  return isBannerHeritageDayVisible ? (
    <div className={styles['bannerContainer']}>
      <a href="https://docsend.com/view/eqbmkrz38ea3i557" target="_blank">
        <Banner className={styles['banner']} />
      </a>
      <CloseButton
        className={styles['openBanner']}
        onClick={() => setIsBannerHeritageDayVisible(false)}
      />
    </div>
  ) : null
}

export default BannerHeritageDay
