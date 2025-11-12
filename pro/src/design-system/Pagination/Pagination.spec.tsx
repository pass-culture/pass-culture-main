import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import * as useMediaQuery from '@/commons/hooks/useMediaQuery'

import { Pagination } from './Pagination'

describe('<Pagination />', () => {
  it('should render without accessibility violations', async () => {
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

    const { container } = render(
      <Pagination currentPage={5} pageCount={10} onPageClick={() => {}} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should give the page number when clicking on the page', () => {
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

    const onPageClick = vi.fn()
    const { getByRole } = render(
      <Pagination currentPage={2} pageCount={5} onPageClick={onPageClick} />
    )

    // Click on page 4 button (should call onPageClick with 4)
    const page4Button = getByRole('button', {
      name: /Aller à la page 4 sur 5/i,
    })
    page4Button.click()
    expect(onPageClick).toHaveBeenCalledWith(4)

    // Click on page 1 button (first page)
    const page1Button = getByRole('button', {
      name: /Aller à la première page/i,
    })
    page1Button.click()
    expect(onPageClick).toHaveBeenCalledWith(1)

    // Click on next page
    const nextButton = getByRole('button', {
      name: /Aller à la page suivante numéro 3/i,
    })
    nextButton.click()
    expect(onPageClick).toHaveBeenCalledWith(3)

    // Click on previous page
    const prevButton = getByRole('button', {
      name: /Aller à la page précédente numéro 1/i,
    })
    prevButton.click()
    expect(onPageClick).toHaveBeenCalledWith(1)

    // Click on last page
    const lastPageButton = getByRole('button', {
      name: /Aller à la dernière page/i,
    })
    lastPageButton.click()
    expect(onPageClick).toHaveBeenCalledWith(5)
  })

  it('should have proper ARIA roles for a11y', () => {
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(false)

    const { getByLabelText, getByRole, getAllByRole } = render(
      <Pagination currentPage={3} pageCount={5} onPageClick={() => {}} />
    )

    // The navigation container should have role="navigation" with proper aria-label
    const nav = getByLabelText('Pagination navigation')
    expect(nav).toBeInTheDocument()
    expect(nav.tagName.toLowerCase()).toBe('nav')

    // There should be a list for the pages
    const list = getByRole('list')
    expect(list.className).toMatch(/pagination-list/)

    // All list items must have role="listitem"
    const items = getAllByRole('listitem')
    expect(items.length).toBeGreaterThan(0)

    // The current page should have aria-current="page"
    const currentPageItem = items.find(
      (item) => item.getAttribute('aria-current') === 'page'
    )
    expect(currentPageItem).toBeDefined()
    expect(getByLabelText(/Page actuelle : 3 sur 5/)).toBeInTheDocument()

    // There should be at least one button with aria-label indicating current page
    const currentPageButton = currentPageItem?.querySelector(
      'button[aria-label*="Page actuelle"]'
    )
    expect(currentPageButton).toBeTruthy()

    // There should be buttons (with appropriate aria-labels) for first, last, previous, next and numbered pages
    expect(
      getByRole('button', { name: /Aller à la page précédente numéro/i })
    ).toBeInTheDocument()
    expect(
      getByRole('button', { name: /Aller à la page suivante numéro/i })
    ).toBeInTheDocument()
    expect(
      getByRole('button', { name: /Aller à la première page/i })
    ).toBeInTheDocument()
    expect(
      getByRole('button', { name: /Aller à la dernière page/i })
    ).toBeInTheDocument()
    expect(
      getByRole('button', { name: /Aller à la page 4 sur 5/i })
    ).toBeInTheDocument()
    expect(
      getByRole('button', { name: /Aller à la page 2 sur 5/i })
    ).toBeInTheDocument()
  })
})
