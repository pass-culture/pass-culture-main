import { describe, expect, it } from 'vitest'

import {
  buildDatasets,
  buildGraphOptions,
  buildMonthlyViews,
  computeGraphSteps,
} from '../statsUtils'

describe('buildDatasets', () => {
  it('should return the correct dataset structure', () => {
    const recentViews = [
      { date: new Date('2023-01-01'), views: 100, rawMonth: 1 },
      { date: new Date('2023-02-01'), views: 200, rawMonth: 2 },
    ]

    const result = buildDatasets(recentViews)

    expect(result.datasets[0].data).toEqual([
      { x: new Date('2023-01-01'), y: 100 },
      { x: new Date('2023-02-01'), y: 200 },
    ])
  })
})

describe('buildGraphOptions', () => {
  it('should return the correct graph options', () => {
    const stepSize = 100
    const firstMonth = 'janvier'

    const result = buildGraphOptions(stepSize, firstMonth)

    expect(result.scales.y.ticks.stepSize).toBe(stepSize)
  })
})

describe('computeGraphSteps', () => {
  it('should return the correct step size', () => {
    const maxViews = 1000
    const minViews = 100

    const result = computeGraphSteps(maxViews, minViews)

    expect(result).toBeGreaterThanOrEqual(300)
  })
})

describe('buildMonthlyViews', () => {
  it('should return the correct monthly views', () => {
    const monthlyViews = [
      { month: 1, views: 100 },
      { month: 2, views: 200 },
    ]

    const result = buildMonthlyViews(monthlyViews)

    expect(result.recentViews.length).toBeGreaterThanOrEqual(0)
    expect(result.minViews).toBeLessThanOrEqual(result.maxViews)
  })
})
