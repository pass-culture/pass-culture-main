import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'

import { type Column, Table, TableVariant } from './Table'

type Row = {
  id: number
  name: string
  email: string
  age: number
  status: 'active' | 'inactive'
  createdAt: string // ISO
  nested: { score: number }
}

const sampleData: Row[] = [
  {
    id: 1,
    name: 'Alice',
    email: 'alice@example.com',
    age: 27,
    status: 'active',
    createdAt: '2024-01-05T10:00:00Z',
    nested: { score: 77 },
  },
  {
    id: 2,
    name: 'Bob',
    email: 'bob@example.com',
    age: 34,
    status: 'inactive',
    createdAt: '2024-02-01T08:30:00Z',
    nested: { score: 65 },
  },
  {
    id: 3,
    name: 'Chloe',
    email: 'chloe@example.com',
    age: 22,
    status: 'active',
    createdAt: '2024-03-12T12:45:00Z',
    nested: { score: 92 },
  },
  {
    id: 4,
    name: 'Diego',
    email: 'diego@example.com',
    age: 41,
    status: 'active',
    createdAt: '2024-04-20T15:10:00Z',
    nested: { score: 58 },
  },
  {
    id: 5,
    name: 'Elise',
    email: 'elise@example.com',
    age: 29,
    status: 'inactive',
    createdAt: '2024-05-11T09:00:00Z',
    nested: { score: 80 },
  },
  {
    id: 6,
    name: 'Fares',
    email: 'fares@example.com',
    age: 37,
    status: 'active',
    createdAt: '2024-06-02T11:15:00Z',
    nested: { score: 71 },
  },
  {
    id: 7,
    name: 'Gina',
    email: 'gina@example.com',
    age: 31,
    status: 'active',
    createdAt: '2024-06-18T16:20:00Z',
    nested: { score: 88 },
  },
  {
    id: 8,
    name: 'Hugo',
    email: 'hugo@example.com',
    age: 25,
    status: 'inactive',
    createdAt: '2024-07-08T07:05:00Z',
    nested: { score: 54 },
  },
]

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })

const baseColumns: Column<Row>[] = [
  {
    id: 'name',
    label: 'Nom',
    sortable: true,
    // Use a function that returns a primitive to sort on
    ordererField: (r: Row) => r.name,
    render: (r: Row) => <strong>{r.name}</strong>,
  },
  {
    id: 'age',
    label: 'Âge',
    sortable: true,
    ordererField: (r: Row) => r.age,
    render: (r: Row) => r.age,
  },
  {
    id: 'created',
    label: 'Créé le',
    sortable: true,
    ordererField: (r: Row) => new Date(r.createdAt).getTime(),
    render: (r: Row) => formatDate(r.createdAt),
  },
  {
    id: 'status',
    label: 'Statut',
    render: (r: Row) => (
      <span aria-label={`status-${r.id}`}>
        {r.status === 'active' ? 'Actif' : 'Inactif'}
      </span>
    ),
  },
  {
    id: 'score',
    label: 'Score',
    sortable: true,
    ordererField: (r: Row) => r.nested.score,
    render: (r: Row) => r.nested.score,
  },
]

// Common props for empty states
const noData = {
  hasNoData: false,
  message: {
    icon: '📄',
    title: 'Aucune donnée',
    subtitle: 'Commencez par créer un élément pour remplir ce tableau.',
  },
}

const noResult = {
  message: 'Aucun résultat pour ces filtres.',
  resetMessage: 'Réinitialiser les filtres',
  onFilterReset: () => alert('reset filters'),
}

const meta: Meta<typeof Table<Row>> = {
  title: 'Design System/Table',
  component: Table<Row>,
  args: {
    title: 'Tableau de données',
    columns: baseColumns,
    data: sampleData,
    selectable: false,
    isLoading: false,
    isSticky: false,
    variant: TableVariant.COLLAPSE,
    noData,
    noResult,
  },
  argTypes: {
    variant: {
      control: 'inline-radio',
      options: [TableVariant.SEPARATE, TableVariant.COLLAPSE],
    },
    isLoading: { control: 'boolean' },
    selectable: { control: 'boolean' },
    isSticky: { control: 'boolean' },
  },
  parameters: {
    layout: 'padded',
  },
}
export default meta

type Story = StoryObj<typeof Table<Row>>

export const Basic: Story = {
  render: (args) => <Table {...args} />,
}

export const SeparateVariant: Story = {
  args: {
    variant: TableVariant.SEPARATE,
  },
}

export const Loading: Story = {
  args: {
    isLoading: true,
  },
}

export const NoResults: Story = {
  args: {
    data: [],
    noData: { ...noData, hasNoData: false },
    noResult: {
      ...noResult,
      onFilterReset: () => alert('Réinitialiser les filtres'),
    },
  },
}

export const NoDataState: Story = {
  args: {
    data: [],
    noData: {
      hasNoData: true,
      message: {
        icon: '📭',
        title: 'Rien à afficher',
        subtitle: 'Aucun élément n’a encore été créé.',
      },
    },
  },
}

export const SelectableUncontrolled: Story = {
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée',
  },
}

export const SelectableControlled: Story = {
  render: (args) => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(
      new Set([2, 4])
    )
    const selectedCount = selectedIds.size
    return (
      <Table
        {...args}
        selectable
        selectedIds={selectedIds}
        selectedNumber={`${selectedCount} sélectionnée${selectedCount > 1 ? 's' : ''}`}
        onSelectionChange={(rows) => {
          setSelectedIds(new Set(rows.map((r) => r.id)))
        }}
      />
    )
  },
}

export const SelectableWithDisabledRows: Story = {
  render: (args) => (
    <Table
      {...args}
      selectable
      isRowSelectable={(row) => row.status === 'active'} // disable inactive rows
      selectedNumber="—"
    />
  ),
}

export const StickyHeaderInScrollContainer: Story = {
  args: { isSticky: true },
  render: (args) => (
    <div style={{ height: 260, overflow: 'auto', border: '1px solid #eee' }}>
      <Table {...args} data={[...sampleData, ...sampleData]} />
    </div>
  ),
}

export const WithHiddenColumns: Story = {
  args: {
    columns: [
      { ...baseColumns[0], headerHidden: true }, // hide header label for "Nom"
      baseColumns[1],
      { ...baseColumns[2], bodyHidden: true }, // hide body cells for "Créé le"
      baseColumns[3],
      baseColumns[4],
    ],
  },
}

export const WithHeaderColSpan: Story = {
  args: {
    columns: [
      { ...baseColumns[0], headerColSpan: 2 }, // spans two header columns
      baseColumns[1],
      baseColumns[2],
      baseColumns[3],
    ],
  },
}

/**
 * Full-row (colspan) detail row
 * Your Table renders a second <tr> with a single <td colSpan=...>
 * whenever getFullRowContent(row) returns a ReactNode.
 */
export const WithFullRowAlwaysDisplayedDetail: Story = {
  render: (args) => {
    const columns: Column<Row>[] = baseColumns

    return (
      <Table
        {...args}
        variant={TableVariant.COLLAPSE}
        columns={columns}
        getFullRowContent={(row) => {
          if (row.age > 30) {
            return (
              <div
                key={row.id}
                style={{
                  padding: '8px',
                  margin: '8px',
                  backgroundColor: 'violet',
                  borderRadius: '4px',
                }}
              >
                {row.name}
              </div>
            )
          }
          return null
        }}
      />
    )
  },
}

/**
 * Full-row (colspan) detail row
 * Your Table renders a second <tr> with a single <td colSpan=...>
 * whenever getFullRowContent(row) returns a ReactNode.
 */
export const WithFullRowDetail: Story = {
  render: (args) => {
    const [expandedId, setExpandedId] = useState<number | null>(3)

    const columns: Column<Row>[] = [
      ...baseColumns.slice(0, 4),
      {
        id: 'actions',
        label: 'Actions',
        render: (r) => (
          <button
            onClick={(e) => {
              e.stopPropagation()
              setExpandedId((prev) => (prev === r.id ? null : r.id))
            }}
          >
            {expandedId === r.id ? 'Fermer' : 'Voir détails'}
          </button>
        ),
      },
    ]

    return (
      <Table
        {...args}
        columns={columns}
        getFullRowContent={(row) =>
          row.id === expandedId ? (
            <div style={{ padding: 16 }}>
              <h4 style={{ margin: 0 }}>{row.name}</h4>
              <p style={{ margin: '8px 0' }}>
                Email: <strong>{row.email}</strong>
              </p>
              <p style={{ margin: 0 }}>
                Score: <strong>{row.nested.score}</strong> — Statut:{' '}
                <strong>{row.status}</strong>
              </p>
            </div>
          ) : null
        }
      />
    )
  },
}

export const SortingShowcase: Story = {
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: (args) => <Table {...args} data={[...sampleData]} />,
}

export const WithPagination: Story = {
  args: {pagination:  { currentPage: 1,
    pageCount: 3,
    onPageClick: (page: number) => { alert(`Go to page ${page}`)  }
  }
  },
  render: (args) => <Table {...args} data={[...sampleData]} />,
}