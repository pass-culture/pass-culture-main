import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import { type Column, Table, TableVariant } from './Table'

vi.mock('@/design-system/Pagination/Pagination', () => ({
  Pagination: ({
    currentPage,
    pageCount,
    onPageClick,
  }: {
    currentPage: number
    pageCount: number
    onPageClick: (page: number) => void
  }) => (
    <nav aria-label="pagination">
      <div data-testid="pagination-props">
        {currentPage}/{pageCount}
      </div>
      <button type="button" onClick={() => onPageClick(1)}>
        page 1
      </button>
      <button type="button" onClick={() => onPageClick(2)}>
        page 2
      </button>
    </nav>
  ),
}))

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

function renderTable(
  overrides: Partial<React.ComponentProps<typeof Table<RowType>>> = {}
) {
  return render(
    <Table<RowType>
      columns={columns}
      data={data}
      isLoading={false}
      variant={TableVariant.COLLAPSE}
      noResult={{
        message: 'Aucun résultat trouvé',
        onFilterReset: vi.fn(),
      }}
      noData={{
        hasNoData: false,
        message: {
          icon: '',
          title: '',
          subtitle: '',
        },
      }}
      {...overrides}
    />
  )
}

describe('<Table />', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders loading skeletons when isLoading is true', () => {
    renderTable({ data: [], isLoading: true })
    expect(
      screen.getAllByRole('row', { name: 'Chargement en cours' }).length
    ).toBeGreaterThan(6)
  })

  it('sorts rows ASC then DESC when clicking on sortable column header twice', async () => {
    renderTable()

    let rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre croissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('1')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre décroissant' })
    )
    rows = screen.getAllByRole('row')
    expect(within(rows[1]).getByText('2')).toBeInTheDocument()
  })

  it('handles row selection and select‑all', async () => {
    const handleSelection = vi.fn()
    renderTable({ selectable: true, onSelectionChange: handleSelection })

    const rowCheckbox = screen.getByLabelText('Alpha')
    await userEvent.click(rowCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])

    const selectAll = screen.getByLabelText(/Tout sélectionner/i)
    await userEvent.click(selectAll)
    expect(handleSelection).toHaveBeenCalledWith(data)
  })

  it('has no accessibility violations', async () => {
    const { container } = renderTable({
      selectable: true,
      title: 'Accessible table',
    })
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('renders no-result message when no data and not loading', () => {
    const onFilterReset = vi.fn()
    renderTable({
      data: [],
      noResult: { message: 'Aucun résultat trouvé', onFilterReset },
    })

    expect(screen.getByText('Aucun résultat trouvé')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Réinitialiser les filtres/i })
    ).toBeInTheDocument()
  })

  it('calls resetFilter when clicking reset button in no-result state', async () => {
    const onFilterReset = vi.fn()
    renderTable({
      data: [],
      noResult: { message: 'Aucun résultat trouvé', onFilterReset },
    })

    const button = screen.getByRole('button', {
      name: /Réinitialiser les filtres/i,
    })
    await userEvent.click(button)
    expect(onFilterReset).toHaveBeenCalledTimes(1)
  })

  it('respects externally controlled selectedIds prop', () => {
    const selectedIds = new Set([1])
    renderTable({ selectable: true, selectedIds })

    const checkbox = screen.getByLabelText('Alpha')
    expect((checkbox as HTMLInputElement).checked).toBe(true)
  })

  it('does not allow selection of non-selectable rows', async () => {
    const handleSelection = vi.fn()
    renderTable({
      selectable: true,
      onSelectionChange: handleSelection,
      isRowSelectable: (row) => row.name !== 'Beta',
    })

    const betaCheckbox = screen.getByLabelText('Beta')
    expect((betaCheckbox as HTMLInputElement).disabled).toBe(true)

    const alphaCheckbox = screen.getByLabelText('Alpha')
    await userEvent.click(alphaCheckbox)
    expect(handleSelection).toHaveBeenCalledWith([data[0]])
  })

  it('renders empty state message when noData.hasNoData is true', () => {
    renderTable({
      data: [],
      noData: {
        hasNoData: true,
        message: {
          icon: 'mock-icon.svg',
          title: 'Aucun justificatif disponible',
          subtitle: 'Les justificatifs apparaîtront ici une fois édités.',
        },
      },
    })

    expect(
      screen.getByText('Aucun justificatif disponible')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Les justificatifs apparaîtront ici une fois édités.')
    ).toBeInTheDocument()
  })

  it('select-all selects every row from allData (across pages), not just the current page', async () => {
    const handleSelection = vi.fn()

    const allData = [
      ...data,
      { id: 3, name: 'Gamma', value: 3 },
      { id: 4, name: 'Delta', value: 4 },
    ]

    renderTable({
      selectable: true,
      allData,
      onSelectionChange: handleSelection,
    })

    await userEvent.click(screen.getByLabelText(/Tout sélectionner/i))

    expect(handleSelection).toHaveBeenLastCalledWith(allData)

    await userEvent.click(screen.getByLabelText(/Tout désélectionner/i))
    expect(handleSelection).toHaveBeenLastCalledWith([])
  })

  it('header checkbox reflects allData and skips non-selectable rows', async () => {
    const handleSelection = vi.fn()

    const page = [
      { id: 1, name: 'A', value: 1 },
      { id: 2, name: 'B', value: 2 },
    ]
    const allData = [
      ...page,
      { id: 3, name: 'C', value: 3 },
      { id: 4, name: 'D', value: 4 },
    ]

    renderTable({
      selectable: true,
      data: page,
      allData,
      isRowSelectable: (r) => r.value % 2 === 1,
      onSelectionChange: handleSelection,
    })

    const header = screen.getByRole('checkbox', { name: /tout sélectionner/i })
    expect(header).not.toBeChecked()

    await userEvent.click(screen.getByLabelText('A'))

    await userEvent.click(header)

    expect(handleSelection).toHaveBeenLastCalledWith([
      { id: 1, name: 'A', value: 1 },
      { id: 3, name: 'C', value: 3 },
    ])
    expect(header).toBeChecked()
  })

  it('respects headerHidden, bodyHidden and headerColSpan', () => {
    const cols: Column<RowType>[] = [
      {
        id: 'hiddenHead',
        label: 'H',
        headerHidden: true,
        ordererField: 'name',
      },
      { id: 'span', label: 'Span', headerColSpan: 2, ordererField: 'value' },
      {
        id: 'hiddenBody',
        label: 'HiddenBody',
        bodyHidden: true,
        ordererField: 'name',
      },
    ]

    renderTable({ columns: cols })

    expect(
      screen.queryByRole('columnheader', { name: 'H' })
    ).not.toBeInTheDocument()

    expect(screen.getByRole('columnheader', { name: 'Span' })).toHaveAttribute(
      'colspan',
      '2'
    )

    const dataRow = screen.getAllByRole('row')[1]
    expect(within(dataRow).queryByText('HiddenBody')).not.toBeInTheDocument()
  })

  it('applies sticky header and variant classes', () => {
    const { container, rerender } = renderTable({
      isSticky: true,
      variant: TableVariant.SEPARATE,
    })
    expect(container.querySelector('thead tr')).toHaveClass(
      'table-header-sticky'
    )
    expect(container.querySelector('table')).toHaveClass('table-separate')

    rerender(
      <Table
        columns={columns}
        data={data}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{ message: 'Aucun résultat trouvé', onFilterReset: vi.fn() }}
        noData={{
          hasNoData: false,
          message: { icon: '', title: '', subtitle: '' },
        }}
      />
    )

    expect(container.querySelector('table')).toHaveClass('table-collapse')
  })

  it('does not render pagination when pagination prop is not provided', () => {
    renderTable({ pagination: undefined })
    expect(
      screen.queryByRole('navigation', { name: /pagination/i })
    ).not.toBeInTheDocument()
  })

  it('renders pagination when pagination prop is provided and forwards currentPage/pageCount', () => {
    renderTable({
      pagination: {
        currentPage: 2,
        pageCount: 5,
        onPageClick: vi.fn(),
      },
    })

    expect(
      screen.getByRole('navigation', { name: /pagination/i })
    ).toBeInTheDocument()
    expect(screen.getByTestId('pagination-props')).toHaveTextContent('2/5')
  })

  it('calls onPageClick when a page is clicked', async () => {
    const onPageClick = vi.fn()

    renderTable({
      pagination: {
        currentPage: 1,
        pageCount: 3,
        onPageClick,
      },
    })

    await userEvent.click(screen.getByRole('button', { name: /page 2/i }))
    expect(onPageClick).toHaveBeenCalledWith(2)
  })
})
