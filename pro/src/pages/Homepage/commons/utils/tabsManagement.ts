import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export const getInitialTab = (
  venueId: number | null,
  hasIndividual: boolean,
  hasCollective: boolean
): string => {
  // The default here is in case something went wrong
  // (no venueId or venue does neither individual nor collective)
  let initialTab: string = 'tab-error'

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
    initialTab = lastVisitedTab || 'tab-individual'
    if (!lastVisitedTab) {
      onNewTabSelected(initialTab, venueId)
    }
  } else if (hasIndividual) {
    initialTab = 'tab-individual'
  } else if (hasCollective) {
    initialTab = 'tab-collective'
  }

  return initialTab
}

export const onNewTabSelected = (
  newSelectedTab: string,
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
