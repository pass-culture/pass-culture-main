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
  checkedStocks: Set<number>
  hasStocks: boolean
  updateCheckedStocks: (newStocks: Set<number>) => void
  deleteStocks: (ids: number[]) => void
  mode: OFFER_WIZARD_MODE
}

export function StocksCalendarActionsBar({
  offerId,
  checkedStocks,
  hasStocks,
  updateCheckedStocks,
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
    return (
      <ActionsBarSticky className={styles['sticky']}>
        <Button as="a" to="/offres" label="Retour à la liste des offres" />
      </ActionsBarSticky>
    )
  }

  return (
    <>
      {checkedStocks.size > 0 ? (
        <ActionsBarSticky className={styles['sticky']}>
          <div className={styles['sticky-content']}>
            <div>
              {checkedStocks.size}{' '}
              {pluralizeFr(
                checkedStocks.size,
                'date sélectionnée',
                'dates sélectionnées'
              )}
            </div>
            <div className={styles['sticky-content-buttons']}>
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  updateCheckedStocks(new Set())
                }}
                label="Désélectionner"
              />
              <Button
                onClick={() => {
                  deleteStocks(Array.from(checkedStocks))
                }}
                label={`Supprimer ${checkedStocks.size > 1 ? 'ces dates' : 'cette date'}`}
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
