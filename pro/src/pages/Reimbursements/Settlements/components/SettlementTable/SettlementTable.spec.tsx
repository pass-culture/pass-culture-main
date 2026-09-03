import { screen } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { axe } from 'vitest-axe'

import { type SettlementResponseModel, SettlementStatus } from '@/apiClient/v1'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SettlementTable } from './SettlementTable'

const baseSettlement = {
  id: 1,
  label: 'VIR001',
  date: '2024-06-01',
  bankAccount: 'Compte principal',
  status: SettlementStatus.EXECUTED,
  amount: 150,
  invoicesCount: 3,
} as SettlementResponseModel

const renderSettlementTable = (
  props: Partial<ComponentProps<typeof SettlementTable>> = {},
  offererOverrides: Partial<typeof defaultGetOffererResponseModel> = {}
) =>
  renderWithProviders(
    <SettlementTable
      settlements={[baseSettlement]}
      isLoading={false}
      hasSettlement={true}
      hasBankAccount={true}
      onFilterReset={noop}
      {...props}
    />,
    {
      storeOverrides: {
        user: {
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            ...offererOverrides,
          },
        },
      },
    }
  )

describe('<SettlementTable />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSettlementTable()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the settlement row with formatted data', () => {
    renderSettlementTable()

    expect(screen.getByRole('cell', { name: 'VIR001' })).toBeVisible()
    expect(screen.getByRole('cell', { name: '01/06/2024' })).toBeVisible()
    expect(screen.getByRole('cell', { name: 'Compte principal' })).toBeVisible()
    expect(screen.getByRole('cell', { name: '3' })).toBeVisible()
    expect(screen.getByRole('cell', { name: 'Virement émis' })).toBeVisible()
    expect(screen.getByRole('cell', { name: /^150,00\s€$/ })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Voir plus' })).toBeVisible()
    const tooltips = screen.getAllByRole('tooltip', { hidden: true })
    expect(tooltips).toHaveLength(2)
    expect(tooltips[0]).toHaveTextContent('Tout sélectionner')
    expect(tooltips[1]).toHaveTextContent('Compte principal')
  })

  it('renders the rejected settlement differently', () => {
    renderSettlementTable({
      settlements: [
        { ...baseSettlement, status: SettlementStatus.REJECTED },
      ] as never,
    })

    expect(screen.queryByRole('cell', { name: '3' })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Voir plus' })
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Remplacer le compte' })
    ).toBeVisible()
  })

  it('displays a dash when the settlement has no date', () => {
    renderSettlementTable({
      settlements: [{ ...baseSettlement, date: null }] as never,
    })

    expect(screen.getByText('-')).toBeVisible()
  })

  it('formats the amount in pacific francs for a Caledonian offerer', () => {
    renderSettlementTable({}, { isCaledonian: true })

    expect(screen.getByText('17 900 F')).toBeVisible()
  })

  it('shows the missing bank account empty state when hasBankAccount is false', () => {
    renderSettlementTable({ hasBankAccount: false })

    expect(screen.getByText('Aucun compte bancaire rattaché')).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Rattacher un compte bancaire' })
    ).toHaveAttribute(
      'href',
      '/administration/remboursements/informations-bancaires'
    )
  })

  it('shows the no-settlement-yet empty state when hasSettlement is false but a bank account exists', () => {
    renderSettlementTable({ hasSettlement: false, settlements: [] })

    expect(screen.getByText('Aucun virement pour le moment')).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Voir mes justificatifs' })
    ).toHaveAttribute('href', '/administration/remboursements/justificatifs')
  })

  it('does not show an empty state when there is at least one settlement and a bank account', () => {
    renderSettlementTable()

    expect(
      screen.queryByText('Aucun virement pour le moment')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Aucun compte bancaire rattaché')
    ).not.toBeInTheDocument()
  })
})
