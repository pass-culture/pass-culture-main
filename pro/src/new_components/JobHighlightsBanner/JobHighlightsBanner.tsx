import React, { useState } from 'react'

import { Banner } from 'ui-kit'

import { ReactComponent as BannerImage } from './assets/job_highlights_banner.svg'
import styles from './JobHighlightsBanner.module.scss'

const JobHighlightsBanner = () => {
  const [isCloseForEver, setIsCloseForEver] = useState(
    localStorage.getItem('iscloseJobHighlights') != null
  )
  const closeForEver = () => {
    localStorage.setItem('iscloseJobHighlights', 'true')
    setIsCloseForEver(localStorage.getItem('iscloseJobHighlights') != null)
  }

  return isCloseForEver ? null : (
    <Banner closable type="image" handleOnClick={closeForEver}>
      <a
        href="https://docsend.com/view/eqbmkrz38ea3i557"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="en savoir plus sur les temps fort des métiers de la culture"
      >
        <BannerImage className={styles['banner-image']} />
      </a>
    </Banner>
  )
}

export default JobHighlightsBanner
