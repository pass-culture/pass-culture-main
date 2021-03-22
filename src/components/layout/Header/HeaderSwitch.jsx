import React from 'react'

import { STYLEGUIDE_ACTIVE } from './_constants'
import HeaderV1 from './HeaderV1'
import HeaderV2 from './HeaderV2'

const HeaderSwitch = ({ isNewHomepageActive, isUserAdmin, ...headerV1Props }) => {
  if (isNewHomepageActive) {
    return (
      <HeaderV2
        isStyleguideActive={STYLEGUIDE_ACTIVE}
        isUserAdmin={isUserAdmin}
      />
    )
  } else {
    return <HeaderV1 {...headerV1Props} />
  }
}

export default HeaderSwitch
