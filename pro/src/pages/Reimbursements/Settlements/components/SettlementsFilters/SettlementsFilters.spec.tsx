import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import type { BankAccountResponseModel } from '@/apiClient/v1'
import { defaultBankAccount } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SettlementsFilters } from './SettlementsFilters'

vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const DEFAULT_INITIAL_ENTRIES = [
  '/?periodBeginningDate=2020-11-15&periodEndingDate=2020-12-15',
]

const BASE_BANK_ACCOUNTS: Array<BankAccountResponseModel> = [
  {
    ...defaultBankAccount,
    id: 1,
    label: 'Compte Principal',
  },
  {
    ...defaultBankAccount,
    id: 2,
    label: 'Compte Secondaire',
  },
]

const renderSettlementsFilters = (
  props = {},
  initialRouterEntries = DEFAULT_INITIAL_ENTRIES
) => {
  const defaultProps = {
    bankAccounts: BASE_BANK_ACCOUNTS,
    onReset: vi.fn(),
    ...props,
  }

  return renderWithProviders(<SettlementsFilters {...defaultProps} />, {
    initialRouterEntries,
  })
}

describe('<SettlementsFilters />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSettlementsFilters()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render form fields correctly', () => {
    renderSettlementsFilters()

    expect(screen.getByLabelText('N° de virement')).toBeInTheDocument()
    expect(screen.getByLabelText('Compte bancaire')).toBeInTheDocument()

    const beginPeriod = screen.getByLabelText('Début de la période')
    const endPeriod = screen.getByLabelText('Fin de la période')

    expect(beginPeriod).toBeInTheDocument()
    expect(beginPeriod).toHaveValue('2020-11-15')

    expect(endPeriod).toBeInTheDocument()
    expect(endPeriod).toHaveValue('2020-12-15')

    expect(
      screen.getByRole('button', { name: 'Lancer la recherche' })
    ).toBeDisabled()
  })

  it('should initialize inputs with URL search params and display reset button', () => {
    renderSettlementsFilters({}, [
      '/?nameSearch=VIR-8888&bankAccountId=2&periodBeginningDate=2020-10-01&periodEndingDate=2020-10-31',
    ])

    expect(screen.getByLabelText('N° de virement')).toHaveValue('VIR-8888')
    expect(screen.getByLabelText('Compte bancaire')).toHaveValue('2')
    expect(screen.getByLabelText('Début de la période')).toHaveValue(
      '2020-10-01'
    )
    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-10-31')

    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Lancer la recherche' })
    ).toBeDisabled()
  })

  it('should enable search button when a filter changes', async () => {
    const user = userEvent.setup()
    renderSettlementsFilters()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()

    const nameInput = screen.getByLabelText('N° de virement')
    await user.type(nameInput, 'VIR-123')

    expect(searchButton).toBeEnabled()
  })

  it('should enable search button when bank account or ending date is modified', async () => {
    const user = userEvent.setup()
    renderSettlementsFilters()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })

    await user.selectOptions(screen.getByLabelText('Compte bancaire'), '1')
    expect(searchButton).toBeEnabled()

    await user.selectOptions(
      screen.getByLabelText('Compte bancaire'),
      'ALL_ACCOUNTS'
    )
    expect(searchButton).toBeDisabled()

    const endPeriod = screen.getByLabelText('Fin de la période')
    await user.clear(endPeriod)
    await user.type(endPeriod, '2020-12-20')
    expect(searchButton).toBeEnabled()
  })

  it('should update search params on search submit', async () => {
    const user = userEvent.setup()
    const { router } = renderSettlementsFilters()

    const nameInput = screen.getByLabelText('N° de virement')
    await user.type(nameInput, 'VIR-2024')

    await user.selectOptions(screen.getByLabelText('Compte bancaire'), '1')

    const beginPeriod = screen.getByLabelText('Début de la période')
    await user.clear(beginPeriod)
    await user.type(beginPeriod, '2020-11-01')

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    await user.click(searchButton)

    await waitFor(() => {
      expect(router.state.location.search).toContain('nameSearch=VIR-2024')
    })
    expect(router.state.location.search).toContain('bankAccountId=1')
    expect(router.state.location.search).toContain(
      'periodBeginningDate=2020-11-01'
    )
  })

  it('should display error message and keep search button disabled when beginning date is empty', async () => {
    const user = userEvent.setup()
    renderSettlementsFilters()

    const beginPeriod = screen.getByLabelText('Début de la période')
    await user.clear(beginPeriod)

    expect(
      screen.getByText('La date de début est obligatoire')
    ).toBeInTheDocument()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()
  })

  it('should display error message and keep search button disabled when ending date is empty', async () => {
    const user = userEvent.setup()
    renderSettlementsFilters()

    const endPeriod = screen.getByLabelText('Fin de la période')
    await user.clear(endPeriod)

    expect(
      screen.getByText('La date de fin est obligatoire')
    ).toBeInTheDocument()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()
  })

  it('should display reset button when custom filters exist and call onReset on click', async () => {
    const user = userEvent.setup()
    const handleReset = vi.fn()

    renderSettlementsFilters({ onReset: handleReset }, [
      '/?nameSearch=VIR-123&bankAccountId=1&periodBeginningDate=2020-10-01&periodEndingDate=2020-10-31',
    ])

    const resetButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    expect(resetButton).toBeInTheDocument()

    await user.click(resetButton)

    expect(handleReset).toHaveBeenCalledTimes(1)
  })

  it('should display reset button when bank account is filtered in URL and reset search params on click', async () => {
    const user = userEvent.setup()
    const handleReset = vi.fn()

    renderSettlementsFilters({ onReset: handleReset }, [
      '/?bankAccountId=1&periodBeginningDate=2020-11-15&periodEndingDate=2020-12-15',
    ])

    const resetButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    expect(resetButton).toBeInTheDocument()

    await user.click(resetButton)

    expect(handleReset).toHaveBeenCalledTimes(1)
  })
})
