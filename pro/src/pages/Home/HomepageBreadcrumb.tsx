import React, { MutableRefObject } from 'react'

import Breadcrumb, { BreadcrumbStyle, Step } from 'components/Breadcrumb'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'

import { doesUserPreferReducedMotion } from '../../utils/windowMatchMedia'

export const STEP_ID_OFFERERS = 'offerers'
const STEP_ID_PROFILE = 'profile'
const STEP_ID_STATS = 'offererStats'
export const STEP_OFFERER_HASH = 'structures'
export const STEP_PROFILE_HASH = 'profil'
export const STEP_STATS_HASH = 'offererStats'

interface HomepageBreadcrumbProps {
  activeStep: string
  profileRef: MutableRefObject<any>
  statsRef: MutableRefObject<any>
  isOffererStatsActive?: boolean
}

const HomepageBreadcrumb = ({
  activeStep,
  profileRef,
  statsRef,
  isOffererStatsActive = false,
}: HomepageBreadcrumbProps) => {
  const { logEvent } = useAnalytics()
  const jumpToProfileSection = (e: React.MouseEvent) => {
    e.preventDefault()
    logEvent?.(Events.CLICKED_BREADCRUMBS_PROFILE_AND_HELP)

    profileRef?.current.scrollIntoView({
      behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
    })
  }
  const jumpToStatsSection = (e: React.MouseEvent) => {
    e.preventDefault()
    logEvent?.(Events.CLICKED_BREADCRUMBS_OFFERER_STATS)

    statsRef?.current.scrollIntoView({
      behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
    })
  }

  const steps: Step[] = [
    {
      id: STEP_ID_OFFERERS,
      label: 'Structures et lieux',
      hash: STEP_OFFERER_HASH,
      onClick: () => logEvent?.(Events.CLICKED_BREADCRUMBS_STRUCTURES),
    },
    {
      id: STEP_ID_PROFILE,
      label: 'Profil et aide',
      hash: STEP_PROFILE_HASH,
      onClick: jumpToProfileSection,
    },
  ]

  if (isOffererStatsActive) {
    steps.splice(1, 0, {
      id: STEP_ID_STATS,
      label: 'Statistiques',
      hash: STEP_STATS_HASH,
      onClick: jumpToStatsSection,
    })
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={Object.values(steps)}
      styleType={BreadcrumbStyle.TAB}
      className="pc-breadcrumb"
    />
  )
}

export default HomepageBreadcrumb
