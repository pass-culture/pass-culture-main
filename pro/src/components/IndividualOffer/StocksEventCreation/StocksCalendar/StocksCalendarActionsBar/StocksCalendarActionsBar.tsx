import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from 'commons/hooks/useNotification'
import { pluralize } from 'commons/utils/pluralize'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

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
  const notify = useNotification()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  function handlePreviousStep() {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        getIndividualOfferUrl({
          offerId: offerId,
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
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
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
        isOnboarding,
      })
    )
  }

  async function handleNextStep() {
    // Check that there is at least one stock left
    if (!hasStocks) {
      notify.error('Veuillez renseigner au moins une date')
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offerId])
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offerId,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
        isOnboarding,
      })
    )
  }

  if (mode === OFFER_WIZARD_MODE.READ_ONLY) {
    return (
      <ActionsBarSticky className={styles['sticky']}>
        <ButtonLink to="/offres" variant={ButtonVariant.PRIMARY}>
          Retour à la liste des offres
        </ButtonLink>
      </ActionsBarSticky>
    )
  }

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
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            handleNextStep()
          }}
          step={OFFER_WIZARD_STEP_IDS.STOCKS}
          dirtyForm={false}
        />
      )}
    </>
  )
}
