import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'

import { doesUserPreferReducedMotion } from '../../../utils/windowMatchMedia'

export const STEP_ID_OFFERERS = 'offerers'
export const STEP_ID_PROFILE = 'profile'
export const STEP_OFFERER_HASH = 'structures'
export const STEP_PROFILE_HASH = 'profil'

const HomepageBreadcrumb = ({ activeStep, profileRef }) => {
  const jumpToProfileSection = e => {
    e.preventDefault()

    profileRef?.current.scrollIntoView({
      behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
    })
  }

  const steps = {
    [STEP_ID_OFFERERS]: {
      id: STEP_ID_OFFERERS,
      label: 'Structures',
      hash: STEP_OFFERER_HASH,
    },
    [STEP_ID_PROFILE]: {
      id: STEP_ID_PROFILE,
      label: 'Profil et aide',
      hash: STEP_PROFILE_HASH,
      onClick: jumpToProfileSection,
    },
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={Object.values(steps)}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

HomepageBreadcrumb.defaultProps = {
  profileRef: null,
}

HomepageBreadcrumb.propTypes = {
  activeStep: PropTypes.string.isRequired,
  profileRef: PropTypes.shape(),
}

export default HomepageBreadcrumb
