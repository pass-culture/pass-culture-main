import { renderHook } from '@testing-library/react'
import { Provider } from 'react-redux'
import * as reactRouter from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { makeUseLocationReturn } from '@/commons/utils/tests/mocks/react-router'

import { useCollectiveOffersSwrKeys } from '../useCollectiveOffersSwrKeys'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

const STORAGE_KEY = 'COLLECTIVE_OFFERS_FILTER_CONFIG'
const TEMPLATE_STORAGE_KEY = 'TEMPLATE_OFFERS_FILTER_CONFIG'

const renderUseCollectiveOffersSwrKeys = (
  isInTemplateOffersPage: boolean,
  features: string[] = []
) => {
  const store = configureTestStore({
    features: {
      list: features.map((name, index) => ({
        id: index,
        name,
        isActive: true,
      })),
    },
    user: {
      selectedPartnerVenue: defaultGetVenue,
    },
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  )

  return renderHook(
    () => useCollectiveOffersSwrKeys({ isInTemplateOffersPage }),
    { wrapper }
  )
}

describe('useCollectiveOffersSwrKeys', () => {
  beforeEach(() => {
    sessionStorage.clear()

    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      makeUseLocationReturn({ search: '' })
    )
  })

  it('should include filters stored in sessionStorage even when URL has no filters', () => {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        storedFilters: {
          status: [CollectiveOfferDisplayedStatus.BOOKED],
        },
        storedVenueId: defaultGetVenue.id,
      })
    )

    const { result } = renderUseCollectiveOffersSwrKeys(false)

    expect(result.current[1].status).toEqual([
      CollectiveOfferDisplayedStatus.BOOKED,
    ])
  })

  it('should produce an identical key for two callers sharing the same state (fetch/mutate parity)', () => {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        storedFilters: {
          status: [CollectiveOfferDisplayedStatus.PREBOOKED],
        },
        storedVenueId: defaultGetVenue.id,
      })
    )

    const { result: firstCaller } = renderUseCollectiveOffersSwrKeys(false)
    const { result: secondCaller } = renderUseCollectiveOffersSwrKeys(false)

    expect(firstCaller.current).toEqual(secondCaller.current)
  })

  it('should prefer URL filters over stored filters when both are set', () => {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        storedFilters: {
          status: [CollectiveOfferDisplayedStatus.PREBOOKED],
        },
        storedVenueId: defaultGetVenue.id,
      })
    )
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      makeUseLocationReturn({ search: '?status=reservee' })
    )

    const { result } = renderUseCollectiveOffersSwrKeys(false)

    expect(result.current[1].status).toEqual([
      CollectiveOfferDisplayedStatus.BOOKED,
    ])
  })

  it('should use the template storage key when on the template offers page', () => {
    sessionStorage.setItem(
      TEMPLATE_STORAGE_KEY,
      JSON.stringify({
        storedFilters: {
          status: [CollectiveOfferDisplayedStatus.PUBLISHED],
        },
        storedVenueId: defaultGetVenue.id,
      })
    )

    const { result } = renderUseCollectiveOffersSwrKeys(true)

    expect(result.current[0]).toEqual('getCollectiveOffersTemplate')
    expect(result.current[1].status).toEqual([
      CollectiveOfferDisplayedStatus.PUBLISHED,
    ])
  })

  it('should use venueId in the key when WIP_SWITCH_VENUE is active', () => {
    const { result } = renderUseCollectiveOffersSwrKeys(false, [
      'WIP_SWITCH_VENUE',
    ])

    expect(result.current[1].venueId).toEqual(String(defaultGetVenue.id))
    expect(result.current[1].offererId).toBeUndefined()
  })
})
