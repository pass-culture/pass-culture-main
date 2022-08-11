import '@testing-library/jest-dom'

import {
  fireEvent,
  render,
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Reimbursements from '../Reimbursements'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  getInvoices: jest.fn(),
  getBusinessUnits: jest.fn(),
  getReimbursementPoints: jest.fn(),
}))

const renderReimbursements = (storeOverride = {}) => {
  const store = configureTestStore(storeOverride)
  const utils = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/remboursements/details']}>
        <Route path="/remboursements" exact={false}>
          <Reimbursements />
        </Route>
      </MemoryRouter>
    </Provider>
  )

  const getElements = () => ({
    nav: {
      refundInvoices: screen.queryByText('Justificatifs de remboursement'),
      refundDetails: screen.queryByText('Détails des remboursements'),
    },
    filters: {
      venue: screen.queryByLabelText('Lieu'),
      periodStart: screen.queryAllByLabelText('début de la période')[0],
      periodEnd: screen.queryAllByLabelText('fin de la période')[0],
    },
    buttons: {
      download: screen.queryByRole('button', {
        name: /Télécharger/i,
      }),
      display: screen.queryByRole('link', {
        name: /Afficher/i,
      }),
      resetFilters: screen.queryByRole('button', {
        name: /Réinitialiser les filtres/i,
      }),
    },
  })

  const expectFilters = filters => {
    const checkValues = async (venue, perdiodStart, periodEnd) => {
      await waitFor(() => expect(filters.venue).toHaveValue(venue))
      await waitFor(() => expect(filters.periodStart).toHaveValue(perdiodStart))
      await waitFor(() => expect(filters.periodEnd).toHaveValue(periodEnd))
    }

    return {
      toHaveInitialValues: async () =>
        await checkValues('allVenues', '15/11/2020', '15/12/2020'),
      toHaveValues: async (venue, perdiodStart, periodEnd) =>
        await checkValues(venue, perdiodStart, periodEnd),
    }
  }

  const setPeriodFilters = (filters, startValue, endValue) => {
    fireEvent.change(filters.periodStart, { target: { value: startValue } })
    fireEvent.change(filters.periodEnd, { target: { value: endValue } })
  }

  const getElementsOnLoadingComplete = async () => {
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    const elements = getElements(storeOverride)

    return {
      ...elements,
      expectFilters: expectFilters(elements.filters),
      setPeriodFilters: (startValue, endValue) =>
        setPeriodFilters(elements.filters, startValue, endValue),
    }
  }

  return {
    ...utils,
    getElementsOnLoadingComplete,
  }
}

const BASE_VENUES = [
  {
    id: 'VENUE1',
    managingOffererId: 'MO1',
    name: 'name venue 1',
    offererName: 'Offerer name venue 1',
    publicName: 'Public Name venue 1',
    isVirtual: false,
    bookingEmail: 'fake@email.com',
    withdrawalDetails: '',
  },
  {
    id: 'VENUE2',
    managingOffererId: 'MO1',
    name: 'Offre numérique',
    offererName: 'Offerer name venue 2',
    publicName: '',
    isVirtual: true,
    bookingEmail: '',
    withdrawalDetails: '',
  },
]

const BASE_INVOICES = [
  {
    id: 'INVOICE1',
    date: '13-01-2022',
    reference: 'ABC',
    businessUnitId: 1,
    amount: 100,
    url: 'url1',
  },
  {
    id: 'INVOICE2',
    date: '13-01-2022',
    reference: 'DEF',
    businessUnitId: 2,
    amount: 100,
    url: 'url2',
  },
]

describe('reimbursementsWithFilters', () => {
  let storeOverride
  let venues
  let invoices

  beforeEach(() => {
    venues = BASE_VENUES
    invoices = BASE_INVOICES
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
    pcapi.getInvoices.mockResolvedValue(invoices)
    pcapi.getBusinessUnits.mockResolvedValue([
      { id: 1, name: 'Point de remboursement 1' },
      { id: 2, name: 'Point de remboursement 2' },
    ])
    pcapi.getReimbursementPoints.mockResolvedValue([])
    storeOverride = {
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: false,
          hasSeenProTutorials: true,
        },
        initialized: true,
      },
    }
  })

  it('should display a refund invoices section', async () => {
    // when
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { nav } = await getElementsOnLoadingComplete()

    // then
    expect(nav.refundInvoices).toBeInTheDocument()
    expect(nav.refundDetails).toBeInTheDocument()
  })

  it('should display the right informations and UI', async () => {
    // given
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { filters, buttons, expectFilters } =
      await getElementsOnLoadingComplete()

    // then
    expect(filters.venue).toBeInTheDocument()

    const options = await within(filters.venue).findAllByRole('option')
    expect(options).toHaveLength(venues.length + 1)

    expect(filters.periodStart).toBeInTheDocument()
    expect(filters.periodEnd).toBeInTheDocument()

    await expectFilters.toHaveInitialValues()

    expect(buttons.resetFilters).toBeInTheDocument()
    expect(buttons.resetFilters).toBeDisabled()

    expect(buttons.download).toBeInTheDocument()
    expect(buttons.display).toBeInTheDocument()

    expect(buttons.download).toBeEnabled()
    expect(buttons.display).toHaveAttribute(
      'href',
      `/remboursements-details?reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15`
    )
  })

  it('should disable buttons if one or both of the period dates are not filled', async () => {
    // given
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { buttons, expectFilters, setPeriodFilters } =
      await getElementsOnLoadingComplete()

    // when
    setPeriodFilters('', '')

    // then
    await expectFilters.toHaveValues('allVenues', '', '')
    expect(buttons.download).toBeDisabled()
    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )

    // when
    setPeriodFilters('12/11/2020', '')

    // then
    await expectFilters.toHaveValues('allVenues', '12/11/2020', '')
    expect(buttons.download).toBeDisabled()
    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )

    // when
    setPeriodFilters('12/11/2020', '12/12/2020')

    // then
    await expectFilters.toHaveValues('allVenues', '12/11/2020', '12/12/2020')
    expect(buttons.download).toBeEnabled()
    expect(buttons.display).toBeEnabled()
  })

  it('should disable buttons if user is admin and no venue filter is selected', async () => {
    // given
    storeOverride.user.currentUser.isAdmin = true
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { buttons, filters } = await getElementsOnLoadingComplete()

    // then
    expect(buttons.download).toBeDisabled()
    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )

    // when
    const options = await within(filters.venue).findAllByRole('option')
    await userEvent.selectOptions(filters.venue, [options[1].value])

    // then
    expect(buttons.download).toBeEnabled()
    expect(screen.getByRole('link', { name: /Afficher/ })).toHaveAttribute(
      'href',
      `/remboursements-details?reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15&venueId=VENUE2`
    )
  })

  it('should reset filters values when clicking on the button', async () => {
    // given
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { filters, buttons, expectFilters, setPeriodFilters } =
      await getElementsOnLoadingComplete()

    // then
    expect(buttons.resetFilters).toBeDisabled()

    // when
    const options = await within(filters.venue).findAllByRole('option')
    setPeriodFilters('12/11/1998', '12/12/1999')
    await userEvent.selectOptions(filters.venue, [options[1].value])

    // then
    await expectFilters.toHaveValues(
      options[1].value,
      '12/11/1998',
      '12/12/1999'
    )
    expect(buttons.resetFilters).toBeEnabled()

    // when
    await userEvent.click(buttons.resetFilters)
    // then
    await expectFilters.toHaveInitialValues()
  })

  it('should order venue option by alphabetical order, and prefix with managingOfferer name when venue is digital', async () => {
    // given
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { filters } = await getElementsOnLoadingComplete()
    const options = await within(filters.venue).findAllByRole('option')

    // then
    const expectedFirstVirtualOption = `${BASE_VENUES[1].offererName} - Offre numérique`
    const expectedSecondOption = BASE_VENUES[0].publicName
    expect(options[0].textContent).toBe('Tous les lieux')
    expect(options[1].textContent).toStrictEqual(expectedFirstVirtualOption)
    expect(options[2].textContent).toStrictEqual(expectedSecondOption)
  })

  it('should call the right URL and filters when clicking display', async () => {
    // given
    const initialFilterUrlParams =
      'reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15'
    const withVenueFilterUrlParams =
      'reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15&venueId=VENUE2'

    // when
    const { getElementsOnLoadingComplete } = renderReimbursements(storeOverride)
    const { buttons, filters } = await getElementsOnLoadingComplete()

    // then
    expect(buttons.display).toHaveAttribute(
      'href',
      `/remboursements-details?${initialFilterUrlParams}`
    )
    const options = await within(filters.venue).findAllByRole('option')
    await userEvent.selectOptions(filters.venue, [options[1].value])
    expect(buttons.display).toHaveAttribute(
      'href',
      `/remboursements-details?${withVenueFilterUrlParams}`
    )
  })

  it('should display no refunds message when user has no associated venues', async () => {
    // given
    pcapi.getVenuesForOfferer.mockResolvedValue([])
    await renderReimbursements(storeOverride)

    // when
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    // then
    expect(
      screen.getByText('Aucun remboursement à afficher')
    ).toBeInTheDocument()
  })
})
