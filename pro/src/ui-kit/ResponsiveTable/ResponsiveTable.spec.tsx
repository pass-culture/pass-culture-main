import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('components/StocksEventList/SortArrow', () => ({
  SortArrow: ({ onClick }: { onClick: () => void }) => (
    <button aria-label="sort" onClick={onClick} data-testid="sort-arrow">
      sort
    </button>
  ),
}))

vi.mock('design-system/Checkbox/Checkbox', () => ({
  Checkbox: ({
    label,
    checked,
    onChange,
    disabled,
    indeterminate,
    ...rest
  }: any) => (
    <input
      type="checkbox"
      aria-label={label}
      aria-checked={indeterminate ? 'mixed' : checked ? 'true' : 'false'}
      checked={checked}
      disabled={disabled}
      onChange={onChange}
      data-testid="checkbox"
      {...rest}
    />
  ),
}))

vi.mock('components/NoResults/NoResults', () => ({
  NoResults: () => <div>No results</div>,
}))

// ---------------------------------------------------------------------------
import { ResponsiveTable } from './ResponsiveTable'

interface Row {
  id: number
  name: string
  value: number
}

const columns = [
  { id: 'name', label: 'Name', sortable: true, accessor: 'name' as keyof Row },
  {
    id: 'value',
    label: 'Value',
    sortable: true,
    accessor: 'value' as keyof Row,
  },
]

const data: Row[] = [
  { id: 1, name: 'Apple', value: 10 },
  { id: 2, name: 'Banana', value: 5 },
]

// ---------------------------------------------------------------------------
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

// ---------------------------------------------------------------------------

describe('<ResponsiveTable />', () => {
  it('renders all rows provided in the data array', () => {
    render(<ResponsiveTable<Row> columns={columns} data={data} />)

    // Both names should appear in the document
    expect(screen.getByText('Apple')).toBeInTheDocument()
    expect(screen.getByText('Banana')).toBeInTheDocument()
  })

  it('sorts rows when a sortable column header arrow is clicked', async () => {
    const user = userEvent.setup()

    render(<ResponsiveTable<Row> columns={columns} data={data} />)

    // Click the second sort arrow (the one for the "Value" column)
    const arrows = screen.getAllByTestId('sort-arrow')
    await user.click(arrows[1])

    // After ascending sort on "Value", Banana (5) should come before Apple (10)
    const nameCells = screen.getAllByRole('cell', { name: /apple|banana/i })
    expect(nameCells[0]).toHaveTextContent('Banana')
    expect(nameCells[1]).toHaveTextContent('Apple')

    // Click again to toggle to descending order
    await user.click(arrows[1])
    const nameCellsDesc = screen.getAllByRole('cell', { name: /apple|banana/i })
    expect(nameCellsDesc[0]).toHaveTextContent('Apple')
    expect(nameCellsDesc[1]).toHaveTextContent('Banana')
  })

  it('emits onSelectionChange when rows are (de)selected', async () => {
    const user = userEvent.setup()
    const handleSelectionChange = vi.fn()

    render(
      <ResponsiveTable<Row>
        columns={columns}
        data={data}
        selectable
        onSelectionChange={handleSelectionChange}
      />
    )

    // Click the "select all" checkbox (labelled by our stub as "Tout sélectionner")
    const selectAllCheckbox = screen.getAllByTestId('checkbox')[0]
    await user.click(selectAllCheckbox)

    expect(handleSelectionChange).toHaveBeenCalledTimes(1)
    expect(handleSelectionChange).toHaveBeenLastCalledWith(data)

    // Deselect first row only
    const rowCheckbox = screen.getAllByLabelText('Apple')[0]
    await user.click(rowCheckbox)

    expect(handleSelectionChange).toHaveBeenCalledTimes(2)
    expect(handleSelectionChange).toHaveBeenLastCalledWith([
      { id: 2, name: 'Banana', value: 5 },
    ])
  })
})
