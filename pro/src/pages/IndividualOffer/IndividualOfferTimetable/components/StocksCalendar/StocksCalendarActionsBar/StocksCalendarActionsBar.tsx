import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import styles from './StocksCalendarActionsBar.module.scss'

export type StocksCalendarActionsBarProps = {
  offerId: number
  hasStocks: boolean
  selectedStocksIds: Set<string | number>
  setSelectedStocksIds: (newStocks: Set<number>) => void
  deleteStocks: (ids: number[]) => void
  mode: OFFER_WIZARD_MODE
}

export function StocksCalendarActionsBar({
  offerId,
  hasStocks,
  selectedStocksIds,
  setSelectedStocksIds,
  deleteStocks,
  mode,
}: StocksCalendarActionsBarProps) {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  function handlePreviousStep() {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offerId,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
      return
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
        isOnboarding,
      })
    )
  }

  async function handleNextStep() {
    // Check that there is at least one stock left
    if (!hasStocks) {
      snackBar.error('Veuillez renseigner au moins une date')
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offerId])
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
        mode,
        isOnboarding,
      })
    )
  }

  if (mode === OFFER_WIZARD_MODE.READ_ONLY) {
    return
  }

  return (
    <>
      {selectedStocksIds.size > 0 ? (
        <ActionsBarSticky className={styles['sticky']}>
          <div className={styles['sticky-content']}>
            <div>
              {selectedStocksIds.size}{' '}
              {pluralizeFr(
                selectedStocksIds.size,
                'date sélectionnée',
                'dates sélectionnées'
              )}
            </div>
            <div className={styles['sticky-content-buttons']}>
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  setSelectedStocksIds(new Set())
                }}
                label="Désélectionner"
              />
              <Button
                onClick={() => {
                  deleteStocks(Array.from(selectedStocksIds))
                }}
                label={`Supprimer ${selectedStocksIds.size > 1 ? 'ces dates' : 'cette date'}`}
              ></Button>
            </div>
          </div>
        </ActionsBarSticky>
      ) : (
        <ActionBar
          onClickPrevious={handlePreviousStep}
          onClickNext={() => {
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            handleNextStep()
          }}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE}
          dirtyForm={false}
          isEvent={true}
        />
      )}
    </>
  )
}
