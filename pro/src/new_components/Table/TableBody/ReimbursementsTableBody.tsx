import React from 'react'

import styles from './ReimbursementsTableBody.module.scss'

type ColumnData = {
  date: string
  businessUnitName: string
  reference: string
  amount: string
}

interface ITableBody {
  invoices: Array<ColumnData>
}

const ReimbursementsTableBody = ({ invoices }: ITableBody): JSX.Element => {
  return (
    <tbody className={styles['reimbursement-body']}>
      {invoices.map(invoice => {
        return (
          <tr key={invoice.reference}>
            <td className={styles['date']}>{invoice.date}</td>
            <td className={styles['business-unit']}>
              {invoice.businessUnitName}
            </td>
            <td>{invoice.reference}</td>
            <td className={styles['amount']}>{invoice.amount}€</td>
          </tr>
        )
      })}
    </tbody>
  )
}

export default ReimbursementsTableBody
