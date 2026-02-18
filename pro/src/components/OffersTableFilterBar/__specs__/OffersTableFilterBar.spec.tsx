import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersTableFilterBar } from '../OffersTableFilterBar'

const defaultProps = {
  onReset: vi.fn(),
}

const renderOffersTableFilterBar = (
  props: Partial<React.ComponentProps<typeof OffersTableFilterBar>> = {}
) => {
  renderWithProviders(
    <OffersTableFilterBar {...defaultProps} {...props}>
      <span data-testid="filter-child">Filter content</span>
    </OffersTableFilterBar>
  )
}

describe('OffersTableFilterBar', () => {
  it('should render children', () => {
    renderOffersTableFilterBar()

    expect(screen.getByTestId('filter-child')).toBeInTheDocument()
  })

  it('should render the reset button', () => {
    renderOffersTableFilterBar()

    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeInTheDocument()
  })

  it('should call onReset when the reset button is clicked', async () => {
    const onReset = vi.fn()
    renderOffersTableFilterBar({ onReset })

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(onReset).toHaveBeenCalledOnce()
  })

  it('should be visible by default', () => {
    renderOffersTableFilterBar()

    expect(screen.getByTestId('offers-filter')).toBeVisible()
  })

  it('should be hidden when isHidden is true', () => {
    renderOffersTableFilterBar({ isHidden: true })

    expect(screen.getByTestId('offers-filter')).not.toBeVisible()
  })

  it('should disable the reset button when isDisabled is true', () => {
    renderOffersTableFilterBar({ isDisabled: true })

    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeDisabled()
  })

  it('should set the id on the container element', () => {
    renderOffersTableFilterBar({ id: 'my-filter-bar' })

    expect(screen.getByTestId('offers-filter')).toHaveAttribute(
      'id',
      'my-filter-bar'
    )
  })
})
