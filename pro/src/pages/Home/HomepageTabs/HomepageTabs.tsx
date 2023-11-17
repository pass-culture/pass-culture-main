import React, { RefObject, useState } from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import Tabs from 'ui-kit/Tabs'
import { Tab } from 'ui-kit/Tabs/Tabs'

import { doesUserPreferReducedMotion } from '../../../utils/windowMatchMedia'

import styles from './HomepageTabs.module.scss'

export const TAB_ID_OFFERERS = 'offerers'
export const TAB_ID_HOME_STATS = 'homeStats'
const TAB_ID_PROFILE = 'profile'
const TAB_ID_STATS = 'offererStats'

interface HomepageTabsProps {
  initialActiveTab: string
  offerersRef: RefObject<HTMLElement>
  profileRef: RefObject<HTMLElement>
  statsRef: RefObject<HTMLElement>
  isOffererStatsActive?: boolean
}

const HomepageTabs = ({
  initialActiveTab,
  offerersRef,
  profileRef,
  statsRef,
  isOffererStatsActive = false,
}: HomepageTabsProps) => {
  const { logEvent } = useAnalytics()
  const [activeTab, setActiveTab] = useState(initialActiveTab)

  const isStatisticsDashboardEnabled = useActiveFeature('WIP_HOME_STATS')

  function jumpToSection(
    e: React.MouseEvent,
    sectionKey: string,
    logEventName: Events,
    targetElement?: HTMLElement | null
  ) {
    e.preventDefault()
    setActiveTab(sectionKey)
    logEvent?.(logEventName)

    targetElement?.scrollIntoView({
      behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
    })
  }

  const tabs: Tab[] = []

  if (isStatisticsDashboardEnabled) {
    tabs.push({
      key: TAB_ID_HOME_STATS,
      label: 'Votre présence sur le pass Culture',
      onClick: (e) =>
        jumpToSection(
          e,
          TAB_ID_HOME_STATS,
          Events.CLICKED_BREADCRUMBS_STRUCTURES,
          null
        ),
    })
  }

  tabs.push({
    key: TAB_ID_OFFERERS,
    label: 'Structures et lieux',
    onClick: (e) =>
      jumpToSection(
        e,
        TAB_ID_OFFERERS,
        Events.CLICKED_BREADCRUMBS_STRUCTURES,
        offerersRef?.current
      ),
  })

  if (isOffererStatsActive) {
    tabs.push({
      key: TAB_ID_STATS,
      label: 'Statistiques',
      onClick: (e) =>
        jumpToSection(
          e,
          TAB_ID_STATS,
          Events.CLICKED_BREADCRUMBS_OFFERER_STATS,
          statsRef?.current
        ),
    })
  }

  tabs.push({
    key: TAB_ID_PROFILE,
    label: 'Profil et aide',
    onClick: (e) =>
      jumpToSection(
        e,
        TAB_ID_PROFILE,
        Events.CLICKED_BREADCRUMBS_PROFILE_AND_HELP,
        profileRef?.current
      ),
  })

  return (
    <div className={styles['homepage-tabs']}>
      <Tabs tabs={tabs} selectedKey={activeTab} />
    </div>
  )
}

export default HomepageTabs
