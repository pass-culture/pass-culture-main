import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import DialogBox from 'components/DialogBox'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import StocksEventList from 'components/StocksEventList'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { PlusCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ActionBar } from '../ActionBar'
import { upsertStocksEventAdapter } from '../StocksEventEdition/adapters'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

export interface IStocksEventCreationProps {
  offer: IOfferIndividual
}

const getInitialStocks = (offer: IOfferIndividual) =>
  offer.stocks.map((stock): StocksEvent => {
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
      id: stock.id,
      beginningDatetime: stock.beginningDatetime,
      bookingLimitDatetime: stock.bookingLimitDatetime,
      priceCategoryId: stock.priceCategoryId,
      quantity: stock.quantity,
    }
  })

export const StocksEventCreation = ({
  offer,
}: IStocksEventCreationProps): JSX.Element => {
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const { logEvent } = useAnalytics()
  const [stocks, setStocks] = useState<StocksEvent[]>(getInitialStocks(offer))
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { setOffer } = useOfferIndividualContext()
  const notify = useNotification()

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: StocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    const rawStocksToAdd = [...stocks, ...newStocks]
    // deduplicate stocks in th whole list
    const stocksToAdd = rawStocksToAdd.filter((stock1, index) => {
      return (
        rawStocksToAdd.findIndex(
          stock2 =>
            stock1.beginningDatetime === stock2.beginningDatetime &&
            stock1.priceCategoryId === stock2.priceCategoryId
        ) === index
      )
    })
    if (stocksToAdd.length < rawStocksToAdd.length) {
      notify.information(
        'Certaines occurences n’ont pas été ajoutées car elles existaient déjà'
      )
    } else {
      notify.success(
        newStocks.length === 1
          ? '1 nouvelle occurrence a été ajoutée'
          : `${newStocks.length} nouvelles occurrences ont été ajoutées`
      )
    }
    setStocks([...stocksToAdd])
  }

  const handlePreviousStep = () => {
    if (!hasUnsavedStocks) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.STOCKS,
        to: OFFER_WIZARD_STEP_IDS.TARIFS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: offer.id,
      })
    }
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getOfferIndividualUrl({
        offerId: offer.nonHumanizedId,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      })
    )
  }

  const stocksToCreate = stocks.filter(stock => stock.id === undefined)
  const stocksToDelete = offer.stocks.filter(
    s => !stocks.find(stock => stock.id === s.id)
  )

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)

      if (stocksToDelete.length > 0) {
        await Promise.all(
          stocksToDelete.map(s => api.deleteStock(s.nonHumanizedId))
        )
      }

      if (stocks.length < 1) {
        if (saveDraft) {
          notify.success('Brouillon sauvegardé dans la liste des offres')
        } else {
          notify.error('Veuillez renseigner au moins une date')
        }
        return
      }

      const { isOk } = await upsertStocksEventAdapter({
        offerId: offer.nonHumanizedId,
        stocks: stocksToCreate,
      })

      if (isOk) {
        const response = await getOfferIndividualAdapter(offer.nonHumanizedId)
        if (response.isOk) {
          const updatedOffer = response.payload
          setOffer && setOffer(updatedOffer)
        }
        navigate(
          getOfferIndividualUrl({
            offerId: offer.nonHumanizedId,
            step: saveDraft
              ? OFFER_WIZARD_STEP_IDS.STOCKS
              : OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode,
          })
        )
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.STOCKS,
          to: saveDraft
            ? OFFER_WIZARD_STEP_IDS.STOCKS
            : OFFER_WIZARD_STEP_IDS.SUMMARY,
          used: saveDraft
            ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
            : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: offer.id,
        })
        setIsClickingFromActionBar(false)
        notify.success(getSuccessMessage(mode))
      } else {
        notify.error(
          "Une erreur est survenue lors de l'enregistrement de vos stocks."
        )
      }
    }

  const hasUnsavedStocks =
    stocksToCreate.length > 0 || stocksToDelete.length > 0

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
        Icon={PlusCircleIcon}
      >
        Ajouter une ou plusieurs dates
      </Button>

      {stocks.length !== 0 && offer?.priceCategories && (
        <StocksEventList
          className={styles['stock-section']}
          stocks={stocks}
          setStocks={setStocks}
          priceCategories={offer.priceCategories}
          departmentCode={offer.venue.departmentCode}
          offerId={offer.id}
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

      <ActionBar
        isDisabled={isOfferDisabled(offer.status)}
        onClickNext={handleNextStep()}
        onClickPrevious={handlePreviousStep}
        onClickSaveDraft={handleNextStep({ saveDraft: true })}
        step={OFFER_WIZARD_STEP_IDS.STOCKS}
        offerId={offer.id}
      />

      <RouteLeavingGuardOfferIndividual
        when={hasUnsavedStocks && !isClickingFromActionBar}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.STOCKS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            offerId: offer?.id,
          })
        }
      />
    </div>
  )
}
