import { beforeEach, describe, expect, it, vi } from 'vitest'

import type {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { getInitialOffererIdAndVenueId } from '@/commons/store/user/utils/getInitialOffererIdAndVenueId'
import {
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

const makeOffererName = (
  overrides: Partial<GetOffererNameResponseModel> = {}
): GetOffererNameResponseModel =>
  getOffererNameFactory({ id: 42, ...overrides })

describe('getInitialOffererIdAndVenueId', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    window.history.pushState({}, '', '/')
  })

  it('should return offerer id from URL param and set shouldRefetch=true (priority 1)', () => {
    window.history.pushState({}, '', '/?structure=707')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '123')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '999')

    const offererNames = [makeOffererName({ id: 1 })]
    const venues = [makeVenueListItem({ id: 2 })]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBe(707)
    expect(initialVenueId).toBeNull()
  })

  it('should return venue id from local storage when present (priority 2)', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '123')

    const offererNames = [makeOffererName({ id: 1 })]
    // Venue id from local storage must exist in the venues list
    const venues = [
      makeVenueListItem({ id: 123 }),
      makeVenueListItem({ id: 2 }),
    ]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBeNull()
    expect(initialVenueId).toBe(123)
  })

  it('should ignore venue id from local storage if not found in venues and fallback to first venue (priority 4)', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '999')

    const offererNames = [makeOffererName({ id: 1 })]
    const venues = [
      makeVenueListItem({ id: 11 }),
      makeVenueListItem({ id: 22 }),
    ]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBeNull()
    expect(initialVenueId).toBe(11)
  })

  it('should return offerer id from local storage when venue id is absent (priority 3)', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '789')

    const offererNames = [makeOffererName({ id: 789 })]
    const venues = [makeVenueListItem({ id: 2 })]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBe(789)
    expect(initialVenueId).toBeNull()
  })

  it('should ignore offerer id from local storage if not found in offerers and fallback to first venue (priority 4)', () => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '555')

    const offererNames = [
      makeOffererName({ id: 1 }),
      makeOffererName({ id: 2 }),
    ]
    const venues = [
      makeVenueListItem({ id: 33 }),
      makeVenueListItem({ id: 44 }),
    ]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBeNull()
    expect(initialVenueId).toBe(33)
  })

  it('should fall back to the first venue when no ids are in storage (priority 4)', () => {
    const offererNames = [makeOffererName({ id: 1 })]
    const venues = [
      makeVenueListItem({ id: 11 }),
      makeVenueListItem({ id: 22 }),
    ]

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBeNull()
    expect(initialVenueId).toBe(11)
  })

  it('should fall back to the first offerer when no venues exist (priority 5)', () => {
    const offererNames = [
      makeOffererName({ id: 20 }),
      makeOffererName({ id: 21 }),
    ]
    const venues: VenueListItemResponseModel[] = []

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBe(20)
    expect(initialVenueId).toBeNull()
  })

  it('should return null ids when nothing is available (priority 6: new user without offerers nor venues)', () => {
    const offererNames: GetOffererNameResponseModel[] = []
    const venues: VenueListItemResponseModel[] = []

    const { initialOffererId, initialVenueId } = getInitialOffererIdAndVenueId(
      offererNames,
      venues,
      false
    )

    expect(initialOffererId).toBeNull()
    expect(initialVenueId).toBeNull()
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    it('should return venue id from local storage when present and valid', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '123')

      const offererNames = [makeOffererName({ id: 1 })]
      const venues = [
        makeVenueListItem({ id: 123 }),
        makeVenueListItem({ id: 2 }),
      ]

      const { initialOffererId, initialVenueId } =
        getInitialOffererIdAndVenueId(offererNames, venues, true)

      expect(initialOffererId).toBeNull()
      expect(initialVenueId).toBe(123)
    })

    it('should return null ids when venue id from local storage is not found in venues list', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '999')

      const offererNames = [makeOffererName({ id: 1 })]
      const venues = [
        makeVenueListItem({ id: 11 }),
        makeVenueListItem({ id: 22 }),
      ]

      const { initialOffererId, initialVenueId } =
        getInitialOffererIdAndVenueId(offererNames, venues, true)

      expect(initialOffererId).toBeNull()
      expect(initialVenueId).toBeNull()
    })

    it('should return null ids when no venue id is in local storage', () => {
      const offererNames = [makeOffererName({ id: 1 })]
      const venues = [
        makeVenueListItem({ id: 11 }),
        makeVenueListItem({ id: 22 }),
      ]

      const { initialOffererId, initialVenueId } =
        getInitialOffererIdAndVenueId(offererNames, venues, true)

      expect(initialOffererId).toBeNull()
      expect(initialVenueId).toBeNull()
    })

    it('should return null ids when no offerers and no venues exist', () => {
      const offererNames: GetOffererNameResponseModel[] = []
      const venues: VenueListItemResponseModel[] = []

      const { initialOffererId, initialVenueId } =
        getInitialOffererIdAndVenueId(offererNames, venues, true)

      expect(initialOffererId).toBeNull()
      expect(initialVenueId).toBeNull()
    })

    it('should still prioritize URL param over local storage', () => {
      window.history.pushState({}, '', '/?structure=707')
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '123')

      const offererNames = [makeOffererName({ id: 1 })]
      const venues = [makeVenueListItem({ id: 123 })]

      const { initialOffererId, initialVenueId } =
        getInitialOffererIdAndVenueId(offererNames, venues, true)

      expect(initialOffererId).toBe(707)
      expect(initialVenueId).toBeNull()
    })
  })
})
