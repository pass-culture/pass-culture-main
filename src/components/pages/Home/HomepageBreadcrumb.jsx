/* eslint-disable react/prop-types */
import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB } from 'components/layout/Breadcrumb'

export const STEP_ID_OFFERERS = 'offerers'
export const STEP_ID_PROFILE = 'profile'
export const STEP_OFFERER_HASH = 'structures'
export const STEP_PROFILE_HASH = 'profil'

const HomepageBreadcrumb = ({ activeStep, profileRef }) => {
  const jumpToProfileSection = e => {
    e.preventDefault()

    const doesUserPreferReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
      .matches
    profileRef?.current.scrollIntoView({
      behavior: doesUserPreferReducedMotion ? 'auto' : 'smooth',
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
      styleType={STYLE_TYPE_TAB}
    />
  )
}

HomepageBreadcrumb.defaultProps = {
  profileRef: null,
}

HomepageBreadcrumb.propTypes = {
  activeStep: PropTypes.string.isRequired,
  profileRef: PropTypes.element,
}

export default HomepageBreadcrumb
