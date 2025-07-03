import { Meta, StoryObj } from '@storybook/react'

import { Column, ResponsiveTable } from './ResponsiveTable'

// Define sample data type
type Row = {
  id: number
  name: string
  value: number
  description?: string
}

// Sample data
const sampleData: Row[] = [
  { id: 1, name: 'Offre Alpha', value: 20, description: 'Détails de Alpha' },
  { id: 2, name: 'Offre Bravo', value: 10, description: 'Détails de Bravo' },
  {
    id: 3,
    name: 'Offre Charlie',
    value: 30,
    description: 'Détails de Charlie',
  },
]

// Column definitions
const baseColumns: Column<Row>[] = [
  {
    id: 'name',
    label: 'Nom',
    accessor: 'name',
    sortable: true,
  },
  {
    id: 'value',
    label: 'Valeur',
    accessor: 'value',
    sortable: true,
  },
]

// Meta
const meta: Meta<typeof ResponsiveTable<Row>> = {
  title: 'Components/ResponsiveTable',
  component: ResponsiveTable,
  tags: ['autodocs'],
}

export default meta

// 📘 Default table
export const Default: StoryObj<typeof ResponsiveTable<Row>> = {
  args: {
    title: 'Tableau simple',
    columns: baseColumns,
    data: sampleData,
  },
}

// 📘 Selectable rows
export const Selectable: StoryObj<typeof ResponsiveTable<Row>> = {
  args: {
    title: 'Sélection d’offres',
    columns: baseColumns,
    data: sampleData,
    selectable: true,
    onSelectionChange: (rows) =>
      console.log('Selected:', rows.map((r) => r.name).join(', ')),
  },
}

// 📘 Sortable table
export const Sortable: StoryObj<typeof ResponsiveTable<Row>> = {
  args: {
    title: 'Tri activé',
    columns: baseColumns,
    data: sampleData,
  },
}

// 📘 Expanded rows
export const WithExpandedRows: StoryObj<typeof ResponsiveTable<Row>> = {
  args: {
    title: 'Lignes extensibles',
    columns: baseColumns,
    data: sampleData,
    getExpandedContent: (row) => (
      <div style={{ padding: '0.5rem', background: '#f0f0f0' }}>
        <strong>Description :</strong> {row.description}
      </div>
    ),
  },
}

// 📘 No results fallback
export const NoResults: StoryObj<typeof ResponsiveTable<Row>> = {
  args: {
    title: 'Aucun résultat',
    columns: baseColumns,
    data: [],
  },
}
