import { fireEvent, render, screen, within } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Column, ResponsiveTable } from './ResponsiveTable'

/**
 * 𝗠𝗼𝗰𝗸 simple components of your design‑system so the tests stay lightweight.
 */
vi.mock('design-system/Checkbox/Checkbox', () => {
  return {
    Checkbox: ({ label, checked, onChange }: any) => (
      <label>
        <input
          type="checkbox"
          aria-label={label}
          checked={checked}
          onChange={onChange}
        />
      </label>
    ),
  }
})

vi.mock('components/StocksEventList/SortArrow', () => {
  return {
    SortArrow: ({ onClick }: any) => (
      <button data-testid="sort-arrow" aria-label="Trier" onClick={onClick} />
    ),
  }
})

vi.mock('ui-kit/Skeleton/Skeleton', () => {
  return {
    Skeleton: ({ width, height }: any) => (
      <div role="img" aria-label="loading-skeleton" style={{ width, height }} />
    ),
  }
})

// ---------------- Fixtures ------------------
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

// ---------------- Test Suite ----------------
describe('<ResponsiveTable />', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading skeletons when isLoading is true', () => {
    render(<ResponsiveTable<RowType> columns={columns} data={[]} isLoading />)
    expect(
      screen.getAllByRole('img', { name: 'loading-skeleton' }).length
    ).toBeGreaterThan(0)
  })

  it('sorts rows when clicking on sortable column header', () => {
    render(
      <ResponsiveTable<RowType>
        columns={columns}
        data={data}
        isLoading={false}
      />
    )

    // initial order: Alpha (2) then Beta (1)
    const rowsBefore = screen.getAllByRole('row')
    expect(within(rowsBefore[1]).getByText('2')).toBeInTheDocument()

    // click sort arrow
    fireEvent.click(screen.getByTestId('sort-arrow'))

    const rowsAfter = screen.getAllByRole('row')
    expect(within(rowsAfter[1]).getByText('1')).toBeInTheDocument()
  })

  it('handles row selection and select all', () => {
    const handleSelection = vi.fn()
    render(
      <ResponsiveTable<RowType>
        columns={columns}
        data={data}
        selectable
        isLoading={false}
        onSelectionChange={handleSelection}
      />
    )

    // select first row
    const rowCheckbox = screen.getByLabelText('Alpha')
    fireEvent.click(rowCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])

    // select all
    const selectAllCb = screen.getByLabelText(/Tout sélectionner/i)
    fireEvent.click(selectAllCb)
    expect(handleSelection).toHaveBeenCalledWith(data)
  })

  it('navigates to row link on click', () => {
    const assignMock = vi.fn()
    // @ts-expect-error – patch JSDOM location
    delete window.location
    // @ts-expect-error
    window.location = { assign: assignMock }

    render(
      <ResponsiveTable<RowType>
        columns={columns}
        data={data}
        isLoading={false}
        getRowLink={(row) => `/items/${row.id}`}
      />
    )

    const tableRows = screen.getAllByRole('row')
    fireEvent.click(tableRows[1])
    expect(assignMock).toHaveBeenCalledWith('/items/1')
  })

  it('has no accessibility violations (axe)', async () => {
    const { container } = render(
      <ResponsiveTable<RowType>
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
