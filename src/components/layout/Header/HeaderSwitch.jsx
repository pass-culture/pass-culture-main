import React from 'react'

import HeaderV1 from './HeaderV1'
import HeaderV2 from './HeaderV2'

const HeaderSwitch = ({ isNewHomepageActive, ...headerV1Props }) => {
  if (isNewHomepageActive) {
    return <HeaderV2 />
  } else {
    return <HeaderV1 {...headerV1Props} />
  }
}

export default HeaderSwitch
