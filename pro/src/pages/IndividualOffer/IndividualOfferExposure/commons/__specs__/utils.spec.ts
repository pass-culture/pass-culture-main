import { ExposureEventType } from '@/apiClient/v1'

import { isOngoing } from '../utils'

const eventFactory = (endDate: string | null) => ({
  type: ExposureEventType.HEADLINE,
  name: null,
  startDate: '2026-02-14T00:00:00Z',
  endDate,
  viewsOnPeriod: null,
})

describe('isOngoing', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-06-23T00:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should be ongoing when the event has no end date', () => {
    expect(isOngoing(eventFactory(null))).toBe(true)
  })

  it('should be ongoing when the end date is in the future', () => {
    expect(isOngoing(eventFactory('2026-12-31T00:00:00Z'))).toBe(true)
  })

  it('should not be ongoing when the end date has passed', () => {
    expect(isOngoing(eventFactory('2026-03-04T00:00:00Z'))).toBe(false)
  })
})
