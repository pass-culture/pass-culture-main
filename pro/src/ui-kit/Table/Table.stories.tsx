import { Meta, StoryObj } from '@storybook/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'

import { Column, Table, TableVariant } from './Table'

// Define sample data type
type Row = {
  id: number
  name: string
  date: string
  structure: string
  etablissement: string
  description?: string
  displayedStatus: CollectiveOfferDisplayedStatus
}

// Sample data
const sampleData: Row[] = [
  {
    id: 1,
    name: 'REIMBURSED BY AC offer 158 pour eac_2_lieu [BON EAC]',
    date: '02/07/2025',
    structure: 'Tous les établissements',
    description: 'Détails de Alpha',
    etablissement: 'Collége Jean moulin',
    displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
  },
  {
    id: 2,
    name: 'CANCELLED BY AC offer 158 pour eac_2_lieu [BON EAC]',
    date: '04/07/2025',
    structure: 'Tous les établissements',
    description: 'Détails de Bravo',
    etablissement: 'Collége Jean moulin',
    displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
  },
  {
    id: 3,
    name: 'BOOK BY AC offer 158 pour eac_2_lieu [BON EAC]',
    structure: 'Tous les établissements',
    date: '28/08/2025',
    description: 'Détails de Charlie',
    etablissement: 'Collége Jean moulin',
    displayedStatus: CollectiveOfferDisplayedStatus.CANCELLED,
  },
]

// Column definitions
const baseColumns: Column<Row>[] = [
  {
    id: 'name',
    label: "Nom de l'offre",
    accessor: 'name',
    sortable: true,
  },
  {
    id: 'date',
    label: "Date de l'évènement",
    accessor: 'date',
    sortable: true,
  },
  {
    id: 'Structure',
    label: 'Structure',
    accessor: 'structure',
  },
  {
    id: 'etablissement',
    label: 'Établissement',
    accessor: 'etablissement',
  },
  {
    id: 'statut',
    label: 'Statut',
    accessor: 'displayedStatus',
    render: (row) => (
      <CollectiveStatusLabel offerDisplayedStatus={row.displayedStatus} />
    ),
  },
  {
    id: 'action',
    label: 'Actions',
    render: () => '...',
  },
]

// Meta
const meta: Meta<typeof Table<Row>> = {
  title: 'Components/ResponsiveTable',
  component: Table,
  tags: ['autodocs'],
}

export default meta

// 📘 Default table
export const Default: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Tableau simple',
    columns: baseColumns,
    data: sampleData,
  },
}

// 📘 table collapse
export const Collapse: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Tableau simple',
    columns: baseColumns,
    data: sampleData,
    variant: TableVariant.COLLAPSE,
  },
}

// 📘 table separate
export const Separate: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Tableau simple',
    columns: baseColumns,
    data: sampleData,
    variant: TableVariant.SEPARATE,
  },
}

// 📘 Selectable rows
export const Selectable: StoryObj<typeof Table<Row>> = {
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
export const Sortable: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Tri activé',
    columns: baseColumns,
    data: sampleData,
  },
}

// 📘 Sortable table
export const Clickable: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Tri activé',
    columns: baseColumns,
    data: sampleData,
    getRowLink: (row) => `/details/${row.id}`,
  },
}

// 📘 Full rows
export const WithFullRows: StoryObj<typeof Table<Row>> = {
  args: {
    title: 'Lignes extensibles',
    columns: baseColumns,
    data: sampleData,
    getFullRowContent: (row) => (
      <div
        style={{
          padding: '0.5rem',
          background: '#f0f0f0',
          borderBottomLeftRadius: '8px',
          borderBottomRightRadius: '8px',
        }}
      >
        <strong>Description :</strong> {row.description}
      </div>
    ),
  },
}
