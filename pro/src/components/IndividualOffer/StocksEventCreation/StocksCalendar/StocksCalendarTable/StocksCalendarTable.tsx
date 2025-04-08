import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getPriceCategoryName } from 'components/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StocksCalendarTable.module.scss'

export function StocksCalendarTable({
  stocks,
  offer,
  onDeleteStocks,
  checkedStocks,
  updateCheckedStocks,
  departmentCode,
}: {
  stocks: GetOfferStockResponseModel[]
  offer: GetIndividualOfferResponseModel
  onDeleteStocks: (id: number[]) => void
  checkedStocks: Set<number>
  updateCheckedStocks: (newStocks: Set<number>) => void
  departmentCode: string
}) {
  function handleStockCheckboxClicked(stockId: number) {
    const newChecked = new Set(Array.from(checkedStocks))
    if (checkedStocks.has(stockId)) {
      newChecked.delete(stockId)
    } else {
      newChecked.add(stockId)
    }
    updateCheckedStocks(newChecked)
  }

  if (stocks.length === 0) {
    return (
      <div className={styles['no-data']}>
        <SvgIcon
          src={strokeSearchIcon}
          alt=""
          className={styles['no-data-icon']}
        />
        <p className={styles['bold']}>Aucune date trouvée</p>
        <p>
          Vous pouvez modifier vos filtres pour lancer une nouvelle recherche
        </p>
      </div>
    )
  }

  return (
    <div className={styles['container']}>
      <table className={styles['table']}>
        <thead className={styles['thead']}>
          <tr>
            <th className={styles['thead-th']}>
              <div className={styles['thead-th-date']}>
                <Checkbox
                  label={
                    <span className={styles['visually-hidden']}>
                      Sélectionner tous les stocks
                    </span>
                  }
                  partialCheck={
                    checkedStocks.size < stocks.length && checkedStocks.size > 0
                  }
                  checked={checkedStocks.size === stocks.length}
                  onChange={() => {
                    if (checkedStocks.size < stocks.length) {
                      updateCheckedStocks(new Set(stocks.map((s) => s.id)))
                    } else {
                      updateCheckedStocks(new Set())
                    }
                  }}
                  name="select-all"
                />
                Date
              </div>
            </th>
            <th className={styles['thead-th']}>Horaire</th>
            <th className={styles['thead-th']}>Tarif</th>
            <th className={styles['thead-th']}>Place</th>
            <th className={styles['thead-th']}>Date limite de réservation</th>
            <th className={styles['thead-th']}>Actions</th>
          </tr>
        </thead>
        <tbody className={styles['tbody']}>
          {stocks.map((stock) => {
            const priceCaregory = offer.priceCategories?.find(
              (p) => p.id === stock.priceCategoryId
            )

            const checkboxDateLabel = stock.beginningDatetime ? (
              <span className={styles['tbody-td-date']}>
                {new Date(stock.beginningDatetime).toLocaleDateString()}
              </span>
            ) : (
              'Date invalide'
            )

            return (
              <tr key={stock.id} className={styles['tr']}>
                <td className={styles['tbody-td']}>
                  <Checkbox
                    label={checkboxDateLabel}
                    checked={checkedStocks.has(stock.id)}
                    onChange={() => handleStockCheckboxClicked(stock.id)}
                    name="select-stock"
                  />
                </td>
                <td className={styles['tbody-td']}>
                  {stock.beginningDatetime
                    ? formatLocalTimeDateString(
                        stock.beginningDatetime,
                        departmentCode,
                        'HH:mm'
                      )
                    : 'Horaire invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  {priceCaregory
                    ? getPriceCategoryName(priceCaregory)
                    : 'Tarif invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  {stock.quantity === null ? 'Illimité' : stock.quantity}
                </td>
                <td className={styles['tbody-td']}>
                  {stock.bookingLimitDatetime
                    ? new Date(stock.bookingLimitDatetime).toLocaleDateString()
                    : 'Date invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  <ListIconButton
                    icon={fullTrashIcon}
                    tooltipContent="Supprimer le stock"
                    onClick={() => onDeleteStocks([stock.id])}
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
