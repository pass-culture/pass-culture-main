import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB } from 'components/layout/Breadcrumb'

export const STEP_ID_OFFERERS = 'offerers'
export const STEP_ID_PROFILE = 'profile'
export const STEP_ID_USAGES = 'usages'

export const steps = {
  [STEP_ID_OFFERERS]: {
    id: STEP_ID_OFFERERS,
    label: 'Structures',
    hash: 'structures',
  },
  [STEP_ID_PROFILE]: {
    id: STEP_ID_PROFILE,
    label: 'Profil et aide',
    hash: 'profil',
  },
  [STEP_ID_USAGES]: {
    id: STEP_ID_USAGES,
    label: 'Modalités d’usage',
    hash: 'usages',
  },
}

const HomepageBreadcrumb = ({ activeStep }) => {
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={Object.values(steps)}
      styleType={STYLE_TYPE_TAB}
    />
  )
}

Breadcrumb.PropTypess = {
  activeStep: PropTypes.string.isRequired,
}

export default HomepageBreadcrumb
