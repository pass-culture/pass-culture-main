import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveBudgetBanner } from './CollectiveBudgetBanner'

it('should display collective budget banner after 01/01/2026', () => {
  vi.useFakeTimers()
  vi.setSystemTime(new Date('2026-01-01T12:00:00Z'))
  renderWithProviders(<CollectiveBudgetBanner />)

  expect(
    screen.getByText('Part collective du pass Culture 2026')
  ).toBeInTheDocument()
})

it('should not display collective budget banner before 01/01/2026', () => {
  vi.useFakeTimers()
  vi.setSystemTime(new Date('2025-12-31T12:00:00Z'))
  renderWithProviders(<CollectiveBudgetBanner />)

  expect(
    screen.queryByText('Part collective du pass Culture 2026')
  ).not.toBeInTheDocument()
})
