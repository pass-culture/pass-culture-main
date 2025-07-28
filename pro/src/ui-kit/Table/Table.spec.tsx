import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import { Column, Table, TableVariant } from './Table'

interface RowType {
  id: number
  name: string
  value: number
}

const columns: Column<RowType>[] = [
  { id: 'name', label: 'Name', ordererField: 'name' },
  { id: 'value', label: 'Value', ordererField: 'value', sortable: true },
]

const data: RowType[] = [
  { id: 1, name: 'Alpha', value: 2 },
  { id: 2, name: 'Beta', value: 1 },
]

describe('<Table />', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading skeletons when isLoading is true', () => {
    render(
      <Table<RowType>
        columns={columns}
        data={[]}
        isLoading
        selectable={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: function (): void {
            throw new Error('Function not implemented.')
          },
        }}
      />
    )
    expect(
      screen.getAllByRole('row', { name: 'Chargement en cours' }).length
    ).toBeGreaterThan(6)
  })

  it('sorts rows ASC then DESC when clicking on sortable column header twice', async () => {
    render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: function (): void {
            throw new Error('Function not implemented.')
          },
        }}
      />
    )

    // initial order: Alpha (2) then Beta (1)
    let rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()

    // click -> ASC (Beta 1 first)
    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre croissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('1')).toBeInTheDocument()

    // click again -> DESC (Alpha 2 first)
    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre décroissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()
  })

  it('handles row selection and select‑all', async () => {
    const handleSelection = vi.fn()
    render(
      <Table<RowType>
        columns={columns}
        data={data}
        selectable
        isLoading={false}
        onSelectionChange={handleSelection}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: function (): void {
            throw new Error('Function not implemented.')
          },
        }}
      />
    )

    // select first row via its checkbox label
    const rowCheckbox = screen.getByLabelText('Alpha')
    await userEvent.click(rowCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])

    // select all via master checkbox
    const selectAll = screen.getByLabelText(/Tout sélectionner/i)
    await userEvent.click(selectAll)
    expect(handleSelection).toHaveBeenCalledWith(data)
  })

  it('has no accessibility violations', async () => {
    const { container } = render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        selectable
        title="Accessible table"
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: function (): void {
            throw new Error('Function not implemented.')
          },
        }}
      />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('renders no-result message when no data and not loading', () => {
    const onFilterReset = vi.fn()

    render(
      <Table<RowType>
        columns={columns}
        data={[]}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucun résultat trouvé',
          onFilterReset,
        }}
      />
    )

    expect(screen.getByText('Aucun résultat trouvé')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Réinitialiser les filtres/i })
    ).toBeInTheDocument()
  })

  it('calls resetFilter when clicking reset button in no-result state', async () => {
    const onFilterReset = vi.fn()

    render(
      <Table<RowType>
        columns={columns}
        data={[]}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucun résultat trouvé',
          onFilterReset,
        }}
      />
    )

    const button = screen.getByRole('button', {
      name: /Réinitialiser les filtres/i,
    })
    await userEvent.click(button)
    expect(onFilterReset).toHaveBeenCalledTimes(1)
  })

  it('respects externally controlled selectedIds prop', () => {
    const selectedIds = new Set([1])

    render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        selectable
        selectedIds={selectedIds}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: vi.fn(),
        }}
      />
    )

    const checkbox = screen.getByLabelText('Alpha') // id = 1
    expect((checkbox as HTMLInputElement).checked).toBe(true)
  })

  it('does not allow selection of non-selectable rows', async () => {
    const handleSelection = vi.fn()

    render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        selectable
        onSelectionChange={handleSelection}
        isRowSelectable={(row) => row.name !== 'Beta'}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: vi.fn(),
        }}
      />
    )

    const betaCheckbox = screen.getByLabelText('Beta')
    expect((betaCheckbox as HTMLInputElement).disabled).toBe(true)

    const alphaCheckbox = screen.getByLabelText('Alpha')
    await userEvent.click(alphaCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])
  })
})
