import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as instantSearch from 'react-instantsearch'

import { apiAdage } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CustomPagination } from '../Pagination'

const mockRefinePagination = vi.fn()

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logSearchShowMore: vi.fn(),
  },
}))

vi.mock('react-instantsearch', async () => {
  return {
    ...(await vi.importActual('react-instantsearch')),
    usePagination: () => ({
      currentRefinement: 0,
      nbPages: 3,
      refine: mockRefinePagination,
    }),
  }
})

describe('AdagePagination', () => {
  const defaultProps = {
    queryId: '123',
  }
  it('should go to next page', async () => {
    renderWithProviders(<CustomPagination {...defaultProps} />)

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))

    expect(mockRefinePagination).toHaveBeenCalledTimes(1)
  })

  it('should not refine on click previous page button', async () => {
    renderWithProviders(<CustomPagination {...defaultProps} />)

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )

    expect(mockRefinePagination).toHaveBeenCalledTimes(1)
  })

  it('should log on click next page and previous page', async () => {
    vi.spyOn(instantSearch, 'usePagination').mockImplementation(() => ({
      createURL: vi.fn((page) => `/page=${page}`),
      refine: vi.fn(),
      canRefine: true,
      currentRefinement: 1,
      nbHits: 10,
      nbPages: 5,
      pages: [0, 1, 2, 3, 4],
      isFirstPage: true,
      isLastPage: false,
    }))

    renderWithProviders(<CustomPagination {...defaultProps} />)

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )

    expect(apiAdage.logSearchShowMore).toHaveBeenCalledTimes(2)
  })
})
