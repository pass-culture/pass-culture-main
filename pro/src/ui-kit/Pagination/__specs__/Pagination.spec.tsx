import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { Pagination, PaginationProps } from '../Pagination'

const defaultProps: PaginationProps = {
  pageCount: 10,
  currentPage: 3,
  onPreviousPageClick: vi.fn(),
  onNextPageClick: vi.fn(),
}

describe('Pagination', () => {
  it('should move from page to page', async () => {
    const previousPage = vi.fn()
    const nextPage = vi.fn()

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

  it('should return nothing if there is only one page', () => {
    render(<Pagination {...defaultProps} currentPage={1} pageCount={1} />)

    expect(
      screen.queryByRole('button', { name: 'Page suivante' })
    ).not.toBeInTheDocument()
  })
})
