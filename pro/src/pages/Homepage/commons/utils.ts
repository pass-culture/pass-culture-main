import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export const TABS = {
  INDIVIDUAL: 'tab-individual',
  COLLECTIVE: 'tab-collective',
} as const

export type TabKey = (typeof TABS)[keyof typeof TABS]

type LastTabsByVenue = Partial<Record<number, TabKey>>

const getLastTabsByVenue = (): LastTabsByVenue => {
  const lastTabsByVenue = localStorageManager.getJSON<LastTabsByVenue>(
    LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS
  )

  return typeof lastTabsByVenue === 'object' && lastTabsByVenue !== null
    ? lastTabsByVenue
    : {}
}

export const getInitialTab = (
  venueId: number,
  hasIndividual: boolean,
  hasCollective: boolean
): TabKey => {
  let initialTab: TabKey = TABS.INDIVIDUAL
  // Last 2 cases ensure that we never display the wrong panel
  // if the venue only does one part of pass culture
  // (so it does not see tabs)
  if (hasCollective && hasIndividual) {
    // We only use localStorage if tabs are displayed
    const lastVisitedTab = getLastTabsByVenue()[venueId]
    initialTab = lastVisitedTab || TABS.INDIVIDUAL
    if (!lastVisitedTab) {
      onNewTabSelected(initialTab, venueId)
    }
  } else if (hasIndividual) {
    initialTab = TABS.INDIVIDUAL
  } else if (hasCollective) {
    initialTab = TABS.COLLECTIVE
  }

  return initialTab
}

export const onNewTabSelected = (
  newSelectedTab: TabKey,
  venueId: number
): void => {
  const lastTabsByVenue = getLastTabsByVenue()
  lastTabsByVenue[venueId] = newSelectedTab
  localStorageManager.setJSON(
    LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
    lastTabsByVenue
  )
}
