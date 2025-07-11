import { fireEvent, render, screen, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import { Column, Table } from './Table'

interface RowType {
  id: number
  name: string
  value: number
}

const columns: Column<RowType>[] = [
  { id: 'name', label: 'Name', accessor: 'name' },
  { id: 'value', label: 'Value', accessor: 'value', sortable: true },
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
      />
    )
    expect(
      screen.getAllByRole('row', { name: 'Chargement en cours' }).length
    ).toBeGreaterThan(6)
  })

  it('sorts rows ASC then DESC when clicking on sortable column header twice', () => {
    render(<Table<RowType> columns={columns} data={data} isLoading={false} />)

    // initial order: Alpha (2) then Beta (1)
    let rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()

    // click -> ASC (Beta 1 first)
    fireEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre croissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('1')).toBeInTheDocument()

    // click again -> DESC (Alpha 2 first)
    fireEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre décroissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()
  })

  it('handles row selection and select‑all', () => {
    const handleSelection = vi.fn()
    render(
      <Table<RowType>
        columns={columns}
        data={data}
        selectable
        isLoading={false}
        onSelectionChange={handleSelection}
      />
    )

    // select first row via its checkbox label
    const rowCheckbox = screen.getByLabelText('Alpha')
    fireEvent.click(rowCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])

    // select all via master checkbox
    const selectAll = screen.getByLabelText(/Tout sélectionner/i)
    fireEvent.click(selectAll)
    expect(handleSelection).toHaveBeenCalledWith(data)
  })

  it('navigates when clicking a row with getRowLink', () => {
    const assignMock = vi.fn()
    // @ts-expect-error patch JSDOM
    delete window.location
    // @ts-expect-error
    window.location = { assign: assignMock }

    render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        getRowLink={(row) => `/items/${row.id}`}
      />
    )

    const rows = screen.getAllByRole('row')
    fireEvent.click(rows[1])
    expect(assignMock).toHaveBeenCalledWith('/items/1')
  })

  it('has no accessibility violations', async () => {
    const { container } = render(
      <Table<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        selectable
        title="Accessible table"
      />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
