import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import TablePagination from '../TablePagination'

describe('components | TablePagination', () => {
  let props

  beforeEach(() => {
    props = {
      canNextPage: false,
      canPreviousPage: false,
      currentPage: 1,
      previousPage: jest.fn(),
      nbPages: 2,
      nextPage: jest.fn(),
    }
  })

  describe('render', () => {
    it('should display previous button when user can go back to previous page', () => {
      // given
      props.canPreviousPage = true

      // when
      render(<TablePagination {...props} />)
      // then
      const previousButton = screen.getAllByRole('button')[0]
      const previousSvg = screen.getAllByRole('img')[0]
      expect(previousSvg).toHaveAttribute(
        'src',
        expect.stringContaining('ico-left-arrow')
      )
      expect(previousButton).not.toHaveAttribute('disabled')
    })

    it('should display current page position', () => {
      // given
      props.currentPage = 1
      props.nbPages = 2

      // when
      render(<TablePagination {...props} />)

      // then
      expect(screen.getByText('Page 1/2')).toBeInTheDocument()
    })

    it('should display next button when user can go to next page', () => {
      // given
      props.canNextPage = true

      // when
      render(<TablePagination {...props} />)

      // then

      const nextButton = screen.getAllByRole('button')[1]
      const nextSvg = screen.getAllByRole('img')[1]
      expect(nextSvg).toHaveAttribute(
        'src',
        expect.stringContaining('ico-right-arrow')
      )
      expect(nextButton).not.toHaveAttribute('disabled')
    })
  })

  describe('when clicking on buttons', () => {
    it('should go back to previous page when click on previous button', async () => {
      // given
      props.canPreviousPage = true
      render(<TablePagination {...props} />)
      const previousButton = screen.getAllByRole('button')[0]

      // when
      await userEvent.click(previousButton)

      // then
      expect(props.previousPage).toHaveBeenCalledTimes(1)
    })

    it('should go to next page when click on next button', async () => {
      // given
      props.canNextPage = true
      render(<TablePagination {...props} />)
      const nextButton = screen.getAllByRole('button')[1]

      // when
      await userEvent.click(nextButton)

      // then
      expect(props.nextPage).toHaveBeenCalledTimes(1)
    })
  })
})
