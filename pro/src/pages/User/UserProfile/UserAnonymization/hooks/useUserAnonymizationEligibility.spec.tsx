import { renderHook } from '@testing-library/react'
import useSWR, { type SWRResponse } from 'swr'

import { useUserAnonymizationEligibility } from './useUserAnonymizationEligibility'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getProAnonymizationEligibility: vi.fn(),
  },
}))

describe('useUserAnonymizationEligibility', () => {
  const useSWRMock = vi.mocked(useSWR)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns loading state when SWR is loading', () => {
    useSWRMock.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as SWRResponse)

    const { result } = renderHook(() => useUserAnonymizationEligibility())

    expect(result.current.isLoading).toBe(true)
    expect(result.current.isEligible).toBe(false)
    expect(result.current.isSoleUserWithOngoingActivities).toBe(undefined)
  })

  it('returns eligible state and appropriate title when user is eligible', () => {
    useSWRMock.mockReturnValue({
      data: {
        hasSuspendedOfferer: false,
        isOnlyPro: true,
        isSoleUserWithOngoingActivities: false,
      },
      isLoading: false,
    } as SWRResponse)

    const { result } = renderHook(() => useUserAnonymizationEligibility())

    expect(result.current.isLoading).toBe(false)
    expect(result.current.isEligible).toBe(true)
    expect(result.current.isSoleUserWithOngoingActivities).toBe(false)
  })

  it('handles user with suspended offerer', () => {
    useSWRMock.mockReturnValue({
      data: {
        hasSuspendedOfferer: true,
        isOnlyPro: true,
        isSoleUserWithOngoingActivities: false,
      },
      isLoading: false,
    } as SWRResponse)

    const { result } = renderHook(() => useUserAnonymizationEligibility())

    expect(result.current.isEligible).toBe(false)
    expect(result.current.isSoleUserWithOngoingActivities).toBe(false)
  })

  it('handles user that is not only pro', () => {
    useSWRMock.mockReturnValue({
      data: {
        hasSuspendedOfferer: false,
        isOnlyPro: false,
        isSoleUserWithOngoingActivities: false,
      },
      isLoading: false,
    } as SWRResponse)

    const { result } = renderHook(() => useUserAnonymizationEligibility())

    expect(result.current.isEligible).toBe(false)
    expect(result.current.isSoleUserWithOngoingActivities).toBe(false)
  })

  it('handles sole user with ongoing activities', () => {
    useSWRMock.mockReturnValue({
      data: {
        hasSuspendedOfferer: false,
        isOnlyPro: true,
        isSoleUserWithOngoingActivities: true,
      },
      isLoading: false,
    } as SWRResponse)

    const { result } = renderHook(() => useUserAnonymizationEligibility())

    expect(result.current.isEligible).toBe(false)
    expect(result.current.isSoleUserWithOngoingActivities).toBe(true)
  })
})
