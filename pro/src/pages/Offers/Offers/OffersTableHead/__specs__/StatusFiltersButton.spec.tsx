import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { CollectiveOfferStatus } from 'core/OfferEducational/types'
import { ADMINS_DISABLED_FILTERS_MESSAGE } from 'core/Offers/constants'
import { Audience } from 'core/shared/types'

import {
  StatusFiltersButton,
  StatusFiltersButtonProps,
} from '../StatusFiltersButton'

const defaultProps: StatusFiltersButtonProps = {
  applyFilters: vi.fn(),
  audience: Audience.COLLECTIVE,
  updateStatusFilter: vi.fn(),
  disabled: false,
}

describe('StatusFiltersButton', () => {
  it('should add an hidden message with the active status', () => {
    render(
      <StatusFiltersButton
        {...{ ...defaultProps, status: CollectiveOfferStatus.BOOKED }}
      />
    )

    expect(
      screen.getByText('Tri par statut Réservée actif')
    ).toBeInTheDocument()
  })

  it('should not add an hidden message if no active status', () => {
    render(
      <StatusFiltersButton
        {...{ ...defaultProps, audience: Audience.INDIVIDUAL }}
      />
    )

    expect(screen.queryByText(/Tri par statut/)).not.toBeInTheDocument()
  })

  it('should display the status form modal when the status icon is clicked', async () => {
    render(<StatusFiltersButton {...defaultProps} />)

    const statusButton = screen.getByRole('button', {
      name: 'Statut Afficher ou masquer le filtre par statut',
    })
    await userEvent.click(statusButton)

    expect(
      screen.getByRole('group', { name: 'Afficher les offres' })
    ).toBeInTheDocument()
  })

  it('should have a specific title when the button is disabled', () => {
    render(<StatusFiltersButton {...{ ...defaultProps, disabled: true }} />)
    const statusButton = screen.getByRole('button', {
      name: 'Statut Afficher ou masquer le filtre par statut',
    })

    expect(statusButton).toHaveAttribute(
      'title',
      ADMINS_DISABLED_FILTERS_MESSAGE
    )
  })
})
