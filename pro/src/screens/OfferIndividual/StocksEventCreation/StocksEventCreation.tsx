import React, { useState } from 'react'

import DialogBox from 'components/DialogBox'
import StocksEventList from 'components/StocksEventList'
import { IStocksEvent } from 'components/StocksEventList/StocksEventList'
import { IOfferIndividual } from 'core/Offers/types'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

interface IStocksEventCreationProps {
  offer: IOfferIndividual
}

export const StocksEventCreation = ({
  offer,
}: IStocksEventCreationProps): JSX.Element => {
  const offerStocks = offer.stocks.map((stock): IStocksEvent => {
    if (
      stock.beginningDatetime === null ||
      stock.beginningDatetime === undefined ||
      stock.bookingLimitDatetime === null ||
      stock.bookingLimitDatetime === undefined ||
      stock.priceCategoryId === null ||
      stock.priceCategoryId === undefined ||
      stock.quantity === undefined
    ) {
      throw 'Error: this stock is not a stockEvent'
    }
    return {
      beginningDatetime: stock.beginningDatetime,
      bookingLimitDatetime: stock.bookingLimitDatetime,
      priceCategoryId: stock.priceCategoryId,
      quantity: stock.quantity,
    }
  })

  const [stocks, setStocks] = useState<IStocksEvent[]>(offerStocks)

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: IStocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    setStocks([...stocks, ...newStocks])
  }

  return (
    <div className={styles['container']}>
      {stocks.length === 0 && (
        <HelpSection className={styles['help-section']} />
      )}
      <Button
        id="add-recurrence"
        variant={ButtonVariant.PRIMARY}
        type="button"
        onClick={() => setIsRecurrenceModalOpen(true)}
        Icon={MoreCircleIcon}
      >
        Ajouter une récurrence
      </Button>
      {stocks.length !== 0 && offer?.priceCategories && (
        <StocksEventList
          className={styles['stock-section']}
          stocks={stocks}
          priceCategories={offer.priceCategories}
          departmentCode="75"
        />
      )}
      {isRecurrenceModalOpen && (
        <DialogBox
          onDismiss={onCancel}
          hasCloseButton
          labelledBy="add-recurrence"
          extraClassNames={styles['recurrence-modal']}
        >
          <RecurrenceForm
            offer={offer}
            onCancel={onCancel}
            onConfirm={onConfirm}
          />
        </DialogBox>
      )}
    </div>
  )
}
