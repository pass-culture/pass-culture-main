import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { InvoiceResponseModel, VenueListItemResponseModel } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import ReimbursementsDetails from '../ReimbursementsDetails/ReimbursementsDetails'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getVenues: jest.fn(),
    getInvoices: jest.fn(),
  },
}))
const venueId = 12
const BASE_VENUES: VenueListItemResponseModel[] = [
  {
    managingOffererId: 1,
    name: 'name venue 1',
    offererName: 'Offerer name venue 1',
    publicName: 'Public Name venue 1',
    isVirtual: false,
    bookingEmail: 'fake@email.com',
    withdrawalDetails: '',
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: false,
    id: venueId,
  },
  {
    managingOffererId: 1,
    name: 'Offre numérique',
    offererName: 'Offerer name venue 2',
    publicName: '',
    isVirtual: true,
    bookingEmail: '',
    withdrawalDetails: '',
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: false,
    id: 2,
  },
]

const BASE_INVOICES: InvoiceResponseModel[] = [
  {
    date: '13-01-2022',
    reference: 'ABC',
    amount: 100,
    url: 'url1',
    cashflowLabels: [],
  },
  {
    date: '13-01-2022',
    reference: 'DEF',
    amount: 100,
    url: 'url2',
    cashflowLabels: [],
  },
]

describe('reimbursementsWithFilters', () => {
  const storeOverrides = {
    user: {
      currentUser: {
        isAdmin: false,
        hasSeenProTutorials: true,
      },
      initialized: true,
    },
  }

  beforeEach(() => {
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: BASE_VENUES })
    jest.spyOn(api, 'getInvoices').mockResolvedValue(BASE_INVOICES)
  })

  it('should not disable buttons when the period dates are filled', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    expect(
      await screen.findByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeEnabled()
    expect(screen.getByText(/Afficher/)).not.toHaveAttribute(
      'aria-disabled',
      'true'
    )
  })

  it('should disable buttons if user is admin and no venue filter is selected', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides: {
        ...storeOverrides,
        user: { currentUser: { isAdmin: true } },
      },
    })

    expect(
      await screen.findByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeDisabled()
    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )
  })

  it('should enable buttons when admin user selects a venue', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides: {
        ...storeOverrides,
        user: { currentUser: { isAdmin: true } },
      },
    })

    await userEvent.selectOptions(
      await screen.findByLabelText('Lieu'),
      'Public Name venue 1'
    )

    expect(
      await screen.getByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeEnabled()
    expect(screen.getByRole('link', { name: /Afficher/ })).toHaveAttribute(
      'href',
      `/remboursements-details?reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15&venueId=${venueId}`
    )
  })

  it('should reset filters values', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    const startFilter = await screen.findByLabelText('Début de la période')
    const endFilter = screen.getByLabelText('Fin de la période')

    await userEvent.type(startFilter, '1998-11-12')
    await userEvent.type(endFilter, '1999-12-12')
    await userEvent.selectOptions(
      await screen.findByLabelText('Lieu'),
      'Public Name venue 1'
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: /Réinitialiser les filtres/i,
      })
    )

    expect(screen.getByLabelText('Lieu')).toHaveValue('allVenues')
    expect(screen.getByLabelText('Début de la période')).toHaveValue(
      '2020-11-15'
    )
    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-12-15')
  })

  it('should order venue option by alphabetical order', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    const options = await within(
      await screen.findByLabelText('Lieu')
    ).findAllByRole('option')

    expect(options[0].textContent).toBe('Tous les lieux')
    expect(options[1].textContent).toStrictEqual(
      'Offerer name venue 2 - Offre numérique'
    )
    expect(options[2].textContent).toStrictEqual('Public Name venue 1')
  })

  it('should prefix with managingOfferer name when venue is digital', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    const options = await within(
      await screen.findByLabelText('Lieu')
    ).findAllByRole('option')

    expect(options[0].textContent).toBe('Tous les lieux')
    expect(options[1].textContent).toStrictEqual(
      'Offerer name venue 2 - Offre numérique'
    )
  })

  it('should update display button url when changing any filter', async () => {
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    await userEvent.selectOptions(
      await screen.findByLabelText('Lieu'),
      'Public Name venue 1'
    )

    const startInput = screen.getByLabelText('Début de la période')
    const endInput = screen.getByLabelText('Fin de la période')
    await userEvent.clear(startInput)
    await userEvent.clear(endInput)
    await userEvent.type(startInput, '1998-11-12')
    await userEvent.type(endInput, '1999-12-12')

    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'href',
      `/remboursements-details?reimbursementPeriodBeginningDate=1998-11-12&reimbursementPeriodEndingDate=1999-12-12&venueId=${venueId}`
    )
  })

  it('should display no refunds message when user has no associated venues', async () => {
    jest.spyOn(api, 'getVenues').mockResolvedValueOnce({ venues: [] })
    renderWithProviders(<ReimbursementsDetails />, {
      storeOverrides,
    })

    expect(
      await screen.findByText('Aucun remboursement à afficher')
    ).toBeInTheDocument()
  })
})
