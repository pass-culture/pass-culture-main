import React, { useState } from 'react'

import { Banner } from 'ui-kit'

import { ReactComponent as BannerImage } from './assets/job_highlights_banner.svg'
import { CLOSE_JOB_HIGHLIGHTS_BANNER_KEY } from './constants'

const JobHighlightsBanner = () => {
  const [isCloseForEver, setIsCloseForEver] = useState(
    localStorage.getItem(CLOSE_JOB_HIGHLIGHTS_BANNER_KEY) != null
  )
  const closeForEver = () => {
    localStorage.setItem(CLOSE_JOB_HIGHLIGHTS_BANNER_KEY, 'true')
    setIsCloseForEver(
      localStorage.getItem(CLOSE_JOB_HIGHLIGHTS_BANNER_KEY) != null
    )
  }

  return isCloseForEver ? null : (
    <Banner closable type="image" handleOnClick={closeForEver}>
      <a
        href="https://docsend.com/view/n9yniyrtusp82a9m"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="en savoir plus sur les temps fort des métiers de la culture"
      >
        <BannerImage />
      </a>
    </Banner>
  )
}

export default JobHighlightsBanner
