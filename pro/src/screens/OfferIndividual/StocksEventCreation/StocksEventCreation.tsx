import React, { useState } from 'react'

import DialogBox from 'components/DialogBox'
import { IOfferIndividual } from 'core/Offers/types'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

export interface IStocksEventCreationProps {
  offer: IOfferIndividual
}

export const StocksEventCreation = ({
  offer,
}: IStocksEventCreationProps): JSX.Element => {
  const [stocks] = useState(offer.stocks)
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  return (
    <div className={styles['container']}>
      {stocks.length === 0 && (
        <HelpSection className={styles['help-section']} />
      )}

      <Button
        variant={ButtonVariant.PRIMARY}
        type="button"
        onClick={() => setIsRecurrenceModalOpen(true)}
        Icon={MoreCircleIcon}
      >
        Ajouter une récurrence
      </Button>

      {isRecurrenceModalOpen && (
        <DialogBox
          onDismiss={() => setIsRecurrenceModalOpen(false)}
          hasCloseButton
          labelledBy="Lolilol"
          extraClassNames={styles['recurrence-modal']}
        >
          <RecurrenceForm />
        </DialogBox>
      )}
    </div>
  )
}
