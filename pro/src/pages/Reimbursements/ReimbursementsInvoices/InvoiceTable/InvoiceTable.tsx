import React from 'react'

import { InvoiceResponseModel } from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'

import ReimbursementsTable from '../../ReimbursementsTable'

interface InvoiceTableProps {
  invoices: InvoiceResponseModel[]
}

const InvoiceTable = ({ invoices }: InvoiceTableProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const columns = [
    {
      title: 'Date du justificatif',
      sortBy: 'date',
      selfDirection: 'default',
    },
    {
      title: isNewBankDetailsJourneyEnabled
        ? 'Compte bancaire'
        : 'Point de remboursement',
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
