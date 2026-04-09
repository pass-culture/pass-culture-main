import type { LinearScaleOptions, TooltipItem } from 'chart.js'
import { describe, expect, it } from 'vitest'

import {
  buildDatasets,
  buildGraphOptions,
  computeGraphSteps,
} from '../statsUtils'

describe('buildDatasets', () => {
  it('should return the correct dataset structure', () => {
    const recentViews = [
      { date: new Date('2023-01-01'), views: 100, rawDate: '2023-01-01' },
      { date: new Date('2023-02-01'), views: 200, rawDate: '2023-02-01' },
    ]

    const result = buildDatasets(recentViews)

    expect(result.datasets[0].data).toEqual([
      { x: '2023-01-01', y: 100 },
      { x: '2023-02-01', y: 200 },
    ])
  })
})

describe('buildGraphOptions', () => {
  it('should return the correct graph options', () => {
    const stepSizeExpected = 100
    const result = buildGraphOptions(stepSizeExpected, 'janvier')

    const yAxis = result.scales?.y as LinearScaleOptions

    expect(yAxis?.ticks?.stepSize).toBe(stepSizeExpected)
  })
  it('should format the tooltip title correctly in French', () => {
    const result = buildGraphOptions(100, 'janvier')
    const titleCallback = result.plugins?.tooltip?.callbacks?.title as any

    const mockTooltipItem = {
      parsed: {
        x: 1711584000000,
      },
    } as TooltipItem<'line'>

    const formattedDate = titleCallback.call({} as any, [mockTooltipItem])

    expect(formattedDate).toBe('28 mars 2024')
  })
  it('should not return anything in the tooltip if x axis is empty', () => {
    const result = buildGraphOptions(100, 'janvier')
    const titleCallback = result.plugins?.tooltip?.callbacks?.title as any

    const mockTooltipItem = {
      parsed: {
        x: null,
      },
    } as TooltipItem<'line'>

    const formattedDate = titleCallback.call({} as any, [mockTooltipItem])

    expect(formattedDate).toBe('')
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
