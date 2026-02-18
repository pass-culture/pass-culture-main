import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import { getInitialTab, onNewTabSelected } from '../utils'

function getLocalStorageManagerMock(initialValue?: Record<string, unknown>) {
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
  it('should return "tab-individual" if no venue given', () => {
    const localStorageManagerMock = getLocalStorageManagerMock()

    expect(getInitialTab(null, false, true)).toBe('tab-individual')

    expect(localStorageManagerMock.getItem).not.toHaveBeenCalled()
    expect(localStorageManagerMock.setItem).not.toHaveBeenCalled()
  })

  it('should not use localStorage if venue only does either individual or collective', () => {
    const localStorageManagerMock = getLocalStorageManagerMock()

    getInitialTab(CURRENT_VENUE_ID, false, true)

    expect(localStorageManagerMock.getItem).not.toHaveBeenCalled()
    expect(localStorageManagerMock.setItem).not.toHaveBeenCalled()
  })

  it('should read the local storage and write the new value when venue does both', () => {
    const localStorageManagerMock = getLocalStorageManagerMock()

    getInitialTab(CURRENT_VENUE_ID, true, true)

    expect(localStorageManagerMock.getItem).toHaveBeenCalledWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS
    )
    expect(localStorageManagerMock.setItem).toHaveBeenCalledWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
      expect.stringMatching(`{"${CURRENT_VENUE_ID}":"tab-.*"}`)
    )
  })

  describe.each([
    {
      case: 'first visit ever to homepage',
      initialLocalStorageValue: undefined,
      expectedTabWhenBoth: 'individual',
    },
    {
      case: 'first visit for the current venue to homepage',
      initialLocalStorageValue: { [OTHER_VENUE_ID]: 'tab-collective' },
      expectedTabWhenBoth: 'individual',
    },
    {
      case: 'last visit for the current venue to homepage was tab-collective',
      initialLocalStorageValue: { [CURRENT_VENUE_ID]: 'tab-collective' },
      expectedTabWhenBoth: 'collective',
    },
    {
      case: 'last visit for the current venue to homepage was tab-individual',
      initialLocalStorageValue: { [CURRENT_VENUE_ID]: 'tab-individual' },
      expectedTabWhenBoth: 'individual',
    },
  ])('when $case', ({ initialLocalStorageValue, expectedTabWhenBoth }) => {
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
        expectedTab: 'individual',
      },
    ])('should return tab $expectedTab if $scenario', ({
      hasIndividual,
      hasCollective,
      expectedTab,
    }) => {
      getLocalStorageManagerMock(initialLocalStorageValue)

      expect(
        getInitialTab(CURRENT_VENUE_ID, hasIndividual, hasCollective)
      ).toBe(`tab-${expectedTab}`)
    })
  })
})

describe('onNewTabSelected', () => {
  it('should update the tab in local storage when a venueId is given', () => {
    const localStorageManagerMock = getLocalStorageManagerMock()
    onNewTabSelected('tab-individual', CURRENT_VENUE_ID)
    expect(localStorageManagerMock.getItem).toHaveBeenCalledOnce()
    expect(localStorageManagerMock.setItem).toHaveBeenCalledExactlyOnceWith(
      LOCAL_STORAGE_KEY.LAST_VISITED_HOMEPAGE_TABS,
      `{"${CURRENT_VENUE_ID}":"tab-individual"}`
    )
  })

  it('should do nothing when no venueId is given', () => {
    const localStorageManagerMock = getLocalStorageManagerMock()
    onNewTabSelected('tab-individual', null)
    expect(localStorageManagerMock.getItem).not.toHaveBeenCalled()
    expect(localStorageManagerMock.setItem).not.toHaveBeenCalled()
  })
})
