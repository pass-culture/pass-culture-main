import React from 'react'

import { InvoiceResponseModel } from 'apiClient/v1'

import ReimbursementsTable from '../../ReimbursementsTable'

interface IInvoiceTableProps {
  invoices: InvoiceResponseModel[]
}

const InvoiceTable = ({ invoices }: IInvoiceTableProps) => {
  const columns = [
    {
      title: 'Date du justificatif',
      sortBy: 'date',
      selfDirection: 'default',
    },
    {
      title: 'Point de remboursement',
      sortBy: 'reimbursementPointName',
      selfDirection: 'default',
    },
    {
      title: 'N° du justificatif',
      sortBy: 'reference',
      selfDirection: 'default',
    },
    {
      title: 'N° de virement',
      sortBy: 'cashflowLabels',
      selfDirection: 'default',
    },
    {
      title: 'Montant remboursé',
      sortBy: 'amount',
      selfDirection: 'None',
    },
  ]

  return <ReimbursementsTable columns={columns} invoices={invoices} />
}

export default InvoiceTable
