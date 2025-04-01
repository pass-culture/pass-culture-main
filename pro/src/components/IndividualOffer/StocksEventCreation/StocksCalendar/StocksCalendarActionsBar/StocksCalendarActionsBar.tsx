import { useNotification } from 'commons/hooks/useNotification'
import { pluralize } from 'commons/utils/pluralize'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './StocksCalendarActionsBar.module.scss'

export type StocksCalendarActionsBarProps = {
  checkedStocks: Set<number>
  hasStocks: boolean
  updateCheckedStocks: (newStocks: Set<number>) => void
  deleteStocks: (ids: number[]) => void
  handlePreviousStep: () => void
  handleNextStep: () => void
}

export function StocksCalendarActionsBar({
  checkedStocks,
  hasStocks,
  updateCheckedStocks,
  deleteStocks,
  handlePreviousStep,
  handleNextStep,
}: StocksCalendarActionsBarProps) {
  const notify = useNotification()

  return (
    <>
      {checkedStocks.size > 0 ? (
        <ActionsBarSticky className={styles['sticky']}>
          <div className={styles['sticky-content']}>
            <div>{pluralize(checkedStocks.size, 'date sélectionnée')}</div>
            <div className={styles['sticky-content-buttons']}>
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  updateCheckedStocks(new Set())
                }}
              >
                Désélectionner
              </Button>
              <Button
                onClick={() => {
                  deleteStocks(Array.from(checkedStocks))
                }}
              >
                Supprimer {checkedStocks.size > 1 ? 'ces dates' : 'cette date'}
              </Button>
            </div>
          </div>
        </ActionsBarSticky>
      ) : (
        <ActionBar
          onClickPrevious={handlePreviousStep}
          onClickNext={() => {
            if (!hasStocks) {
              notify.error('Veuillez renseigner au moins une date')
              return
            }
            handleNextStep()
          }}
          step={OFFER_WIZARD_STEP_IDS.STOCKS}
          dirtyForm={false}
        />
      )}
    </>
  )
}
