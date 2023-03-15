import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom-v5-compat'

import { api } from 'apiClient/api'
import DialogBox from 'components/DialogBox'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import StocksEventList from 'components/StocksEventList'
import { IStocksEvent } from 'components/StocksEventList/StocksEventList'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { isOfferDisabled } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ActionBar } from '../ActionBar'
import { upsertStocksEventAdapter } from '../StocksEventEdition/adapters'
import { getSuccessMessage } from '../utils'

import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

export interface IStocksEventCreationProps {
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
      id: stock.id,
      beginningDatetime: stock.beginningDatetime,
      bookingLimitDatetime: stock.bookingLimitDatetime,
      priceCategoryId: stock.priceCategoryId,
      quantity: stock.quantity,
    }
  })
  const [stocks, setStocks] = useState<IStocksEvent[]>(offerStocks)
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { setOffer } = useOfferIndividualContext()
  const notify = useNotification()

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: IStocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    setStocks([...stocks, ...newStocks])
  }

  const handlePreviousStep = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      })
    )
  }
  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      const stocksToCreate = stocks.filter(s => s.id === undefined)
      const stocksToDelete = offer.stocks.filter(
        s => !stocks.find(stock => stock.id === s.id)
      )
      const { isOk } = await upsertStocksEventAdapter({
        offerId: offer.id,
        stocks: stocksToCreate,
      })

      if (stocksToDelete.length > 0) {
        await Promise.all(stocksToDelete.map(s => api.deleteStock(s.id)))
      }

      if (isOk) {
        notify.success(getSuccessMessage(mode))
        const response = await getOfferIndividualAdapter(offer.id)
        if (response.isOk) {
          const updatedOffer = response.payload
          setOffer && setOffer(updatedOffer)
        }
        navigate(
          getOfferIndividualUrl({
            offerId: offer.id,
            step: saveDraft
              ? OFFER_WIZARD_STEP_IDS.STOCKS
              : OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode,
          })
        )
      } else {
        notify.error(
          "Une erreur est survenue lors de l'enregistrement de vos stocks."
        )
      }
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
          setStocks={setStocks}
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
      <ActionBar
        isDisabled={isOfferDisabled(offer.status)}
        onClickNext={handleNextStep()}
        onClickPrevious={handlePreviousStep}
        onClickSaveDraft={handleNextStep({ saveDraft: true })}
        step={OFFER_WIZARD_STEP_IDS.STOCKS}
        offerId={offer.id}
      />
    </div>
  )
}
