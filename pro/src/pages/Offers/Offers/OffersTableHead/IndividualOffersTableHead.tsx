import classNames from 'classnames'

export const IndividualOffersTableHead = (): JSX.Element => {
  return (
    <thead>
      <tr>
        <th colSpan={3} />

        <th>Lieu</th>
        <th>Stocks</th>
        <th>Statut</th>
        <th className={classNames('th-actions')}>Actions</th>
      </tr>
    </thead>
  )
}
