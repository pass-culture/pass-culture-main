import React, { useState } from 'react'

import DialogBox from 'components/DialogBox'
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
  const [stocks] = useState(offer.stocks)
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: IStocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    // TODO add new stocks to state
    alert(JSON.stringify(newStocks))
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
