import { fireEvent, screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveBudgetCallout } from './CollectiveBudgetCallout'
import {
  COLLECTIVE_OFFER_CREATION_DESCRIPTION,
  COLLECTIVE_OFFER_CREATION_TITLE,
  COLLECTIVE_TABLES_DESCRIPTION,
  COLLECTIVE_TABLES_TITLE,
} from './constants'

describe('CollectiveBudgetCallout', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should display the callout by default', () => {
    renderWithProviders(<CollectiveBudgetCallout pageName="test-page" />)
    expect(
      screen.getByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).toBeInTheDocument()
    expect(
      screen.getByText(COLLECTIVE_OFFER_CREATION_DESCRIPTION)
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /En savoir plus/ })
    ).toBeInTheDocument()
  })

  it('should display the callout for collective table', () => {
    renderWithProviders(
      <CollectiveBudgetCallout
        pageName="test-page"
        variant="COLLECTIVE_TABLE"
      />
    )
    expect(screen.getByText(COLLECTIVE_TABLES_TITLE)).toBeInTheDocument()
    expect(screen.getByText(COLLECTIVE_TABLES_DESCRIPTION)).toBeInTheDocument()
  })

  it('should not display the callout if already closed in localStorage', () => {
    localStorage.setItem('collective-budget-callout-test-page', 'true')
    renderWithProviders(<CollectiveBudgetCallout pageName="test-page" />)
    expect(
      screen.queryByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).not.toBeInTheDocument()
  })

  it('should close the callout and set localStorage on close', () => {
    renderWithProviders(<CollectiveBudgetCallout pageName="test-page" />)
    const closeButton = screen.getByRole('button')
    fireEvent.click(closeButton)
    expect(
      screen.queryByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).not.toBeInTheDocument()
    expect(localStorage.getItem('collective-budget-callout-test-page')).toBe(
      'true'
    )
  })
})
