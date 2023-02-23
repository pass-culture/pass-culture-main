import React, { useState } from 'react'

import { IOfferIndividual } from 'core/Offers/types'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { HelpSection } from './HelpSection/HelpSection'
import styles from './StocksEventCreation.module.scss'

export interface IStocksEventCreationProps {
  offer: IOfferIndividual
}

export const StocksEventCreation = ({
  offer,
}: IStocksEventCreationProps): JSX.Element => {
  const [stocks] = useState(offer.stocks)

  return (
    <div className={styles['container']}>
      {stocks.length === 0 && (
        <HelpSection className={styles['help-section']} />
      )}

      <Button
        variant={ButtonVariant.PRIMARY}
        type="button"
        Icon={MoreCircleIcon}
      >
        Ajouter une récurrence
      </Button>
    </div>
  )
}
