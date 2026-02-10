import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export const TABS = {
  INDIVIDUAL: 'tab-individual',
  COLLECTIVE: 'tab-collective',
} as const

export type TabKey = (typeof TABS)[keyof typeof TABS]

export const getInitialTab = (
  venueId: number | null,
  hasIndividual: boolean,
  hasCollective: boolean
): TabKey => {
  let initialTab: TabKey = TABS.INDIVIDUAL

  if (venueId === null) {
    return initialTab
  }

  // Last 2 cases ensure that we never display the wrong panel
  // if the venue only does one part of pass culture
  // (so it does not see tabs)
  if (hasCollective && hasIndividual) {
    // We only use localStorage if tabs are displayed
    const lastTabsByVenue = JSON.parse(
      localStorageManager.getItem(
        LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS
      ) ?? '{}'
    )
    const lastVisitedTab = lastTabsByVenue[venueId]
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
  venueId: number | null
): void => {
  if (venueId !== null) {
    const lastTabsByVenue = JSON.parse(
      localStorageManager.getItem(
        LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS
      ) ?? '{}'
    )
    lastTabsByVenue[venueId] = newSelectedTab
    localStorageManager.setItem(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
      JSON.stringify(lastTabsByVenue)
    )
  }
}
