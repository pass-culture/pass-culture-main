import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import { getInitialTab, onNewTabSelected } from '../tabsManagement'

function getLsManager(initialValue?: Record<string, unknown>) {
  return {
    getItem: vi
      .spyOn(localStorageManager, 'getItem')
      .mockReturnValue(initialValue ? JSON.stringify(initialValue) : null),

    setItem: vi.spyOn(localStorageManager, 'setItem'),
  }
}

const CURRENT_VENUE_ID = 12
const OTHER_VENUE_ID = 34

beforeEach(() => {
  vi.resetAllMocks()
})

describe('getInitialTab', () => {
  it('should return "tab-error" if no venue given', () => {
    const ls = getLsManager()

    expect(getInitialTab(undefined, false, true)).toBe('tab-error')

    expect(ls.getItem).not.toHaveBeenCalled()
    expect(ls.setItem).not.toHaveBeenCalled()
  })

  it('should not use localStorage if venue only does either individual or collective', () => {
    const ls = getLsManager()

    getInitialTab(CURRENT_VENUE_ID, false, true)

    expect(ls.getItem).not.toHaveBeenCalled()
    expect(ls.setItem).not.toHaveBeenCalled()
  })

  it('should read the local storage and write the new value when venue does both', () => {
    const ls = getLsManager()

    getInitialTab(CURRENT_VENUE_ID, true, true)

    expect(ls.getItem).toHaveBeenCalledWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS
    )
    expect(ls.setItem).toHaveBeenCalledWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
      expect.stringMatching(`{"${CURRENT_VENUE_ID}":"tab-.*"}`)
    )
  })

  describe.each([
    {
      case: 'first visit ever to homepage',
      initialLsValue: undefined,
      expectedTabWhenBoth: 'individual',
    },
    {
      case: 'first visit for the current venue to homepage',
      initialLsValue: { [OTHER_VENUE_ID]: 'tab-collective' },
      expectedTabWhenBoth: 'individual',
    },
    {
      case: 'other visit for the current venue to homepage',
      initialLsValue: { [CURRENT_VENUE_ID]: 'tab-collective' },
      expectedTabWhenBoth: 'collective',
    },
    {
      case: 'other visit for the current venue to homepage',
      initialLsValue: { [CURRENT_VENUE_ID]: 'tab-individual' },
      expectedTabWhenBoth: 'individual',
    },
  ])('when $case', ({ initialLsValue, expectedTabWhenBoth }) => {
    it.each([
      {
        scenario: 'venue only does individual',
        hasIndividual: true,
        hasCollective: false,
        expectedTab: 'individual',
      },
      {
        scenario: 'venue only does collective',
        hasIndividual: false,
        hasCollective: true,
        expectedTab: 'collective',
      },
      {
        scenario: 'venue does both collective and individual',
        hasIndividual: true,
        hasCollective: true,
        expectedTab: expectedTabWhenBoth,
      },
      {
        scenario: 'venue does neither collective nor individual',
        hasIndividual: false,
        hasCollective: false,
        expectedTab: 'error',
      },
    ])('should return tab $expectedTab if $scenario', ({
      hasIndividual,
      hasCollective,
      expectedTab,
    }) => {
      getLsManager(initialLsValue)

      expect(
        getInitialTab(CURRENT_VENUE_ID, hasIndividual, hasCollective)
      ).toBe(`tab-${expectedTab}`)
    })
  })
})

describe('onNewTabSelected', () => {
  it('should update the tab in local storage when a venueId is given', () => {
    const ls = getLsManager()
    onNewTabSelected('tab-individual', CURRENT_VENUE_ID)
    expect(ls.getItem).toHaveBeenCalledOnce()
    expect(ls.setItem).toHaveBeenCalledExactlyOnceWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
      `{"${CURRENT_VENUE_ID}":"tab-individual"}`
    )
  })

  it('should do nothing when no venueId is given', () => {
    const ls = getLsManager()
    onNewTabSelected('tab-individual', undefined)
    expect(ls.getItem).not.toHaveBeenCalled()
    expect(ls.setItem).not.toHaveBeenCalled()
  })
})
