import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Pagination, PaginationProps } from '../Pagination'

const defaultProps: PaginationProps = {
  pageCount: 10,
  currentPage: 3,
  onPreviousPageClick: jest.fn(),
  onNextPageClick: jest.fn(),
}

describe('Pagination', () => {
  it('should move from page to page', async () => {
    const previousPage = jest.fn()
    const nextPage = jest.fn()

    render(
      <Pagination
        {...defaultProps}
        onPreviousPageClick={previousPage}
        onNextPageClick={nextPage}
      />
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Page précédente' })
    )
    await waitFor(() => expect(previousPage).toHaveBeenCalled())

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    await waitFor(() => expect(nextPage).toHaveBeenCalled())
  })

  it('should disable previous page button on first page', () => {
    render(<Pagination {...defaultProps} currentPage={1} />)

    expect(
      screen.getByRole('button', { name: 'Page précédente' })
    ).toBeDisabled()
  })

  it('should disable next page button on last page', () => {
    render(<Pagination {...defaultProps} currentPage={10} pageCount={10} />)

    expect(screen.getByRole('button', { name: 'Page suivante' })).toBeDisabled()
  })
})
