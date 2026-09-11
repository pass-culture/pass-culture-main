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

export type StocksCalendarActionsBarProps = {
  offerId: number
  checkedStocks: Set<number>
  hasStocks: boolean
  updateCheckedStocks: (newStocks: Set<number>) => void
  deleteStocks: (ids: number[]) => void
}

export function StocksCalendarActionsBar({
  offerId,
  checkedStocks,
  hasStocks,
  updateCheckedStocks,
  deleteStocks,
}: Readonly<StocksCalendarActionsBarProps>) {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  function handlePreviousStep() {
    navigate(
      getIndividualOfferUrl({
        offerId: offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        mode: OFFER_WIZARD_MODE.CREATION,
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
    navigate(
      getIndividualOfferUrl({
        offerId: offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding,
      })
    )
  }

  return (
    <>
      {checkedStocks.size > 0 ? (
        <ActionsBarSticky isEmbedded>
          <ActionsBarSticky.Left>
            {checkedStocks.size}&nbsp;
            {pluralizeFr(
              checkedStocks.size,
              'date sélectionnée',
              'dates sélectionnées'
            )}
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right>
            <Button
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                updateCheckedStocks(new Set())
              }}
              label="Désélectionner"
              fullWidth
            />
            <Button
              onClick={() => {
                deleteStocks(Array.from(checkedStocks))
              }}
              label={`Supprimer ${checkedStocks.size > 1 ? 'ces dates' : 'cette date'}`}
              fullWidth
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      ) : (
        <ActionBar
          onClickPrevious={handlePreviousStep}
          onClickNext={() => {
            handleNextStep()
          }}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE}
          dirtyForm={false}
        />
      )}
    </>
  )
}
