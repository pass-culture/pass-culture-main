import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { v4 as uuidv4 } from 'uuid'

import { api } from 'apiClient/api'
import DialogBox from 'components/DialogBox'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer'
import StocksEventList from 'components/StocksEventList'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import ActionBar from '../ActionBar/ActionBar'
import { MAX_STOCKS_PER_OFFER } from '../constants'
import upsertStocksEventAdapter from '../StocksEventEdition/adapters/upsertStocksEventAdapter'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

export interface StocksEventCreationProps {
  offer: IndividualOffer
}

const getInitialStocks = (offer: IndividualOffer) =>
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
      id: stock?.id ? stock.id.toString() : undefined,
      beginningDatetime: stock.beginningDatetime,
      bookingLimitDatetime: stock.bookingLimitDatetime,
      priceCategoryId: stock.priceCategoryId,
      quantity: stock.quantity,
      uuid: uuidv4(),
    }
  })

export const StocksEventCreation = ({
  offer,
}: StocksEventCreationProps): JSX.Element => {
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const [stocks, setStocks] = useState<StocksEvent[]>(getInitialStocks(offer))
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { setOffer } = useIndividualOfferContext()
  const notify = useNotification()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: StocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    const rawStocksToAdd = [...stocks, ...newStocks]
    // deduplicate stocks in the whole list
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
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      })
    )
  }
  const stocksToCreate = stocks
    .filter(stock => stock.id === undefined)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .map(({ uuid, ...rest }) => rest)
  const stocksToDelete = offer.stocks.filter(
    s =>
      !stocks.find(stock => stock.id === (s?.id ? s.id.toString() : undefined))
  )

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsSubmitting(true)
      setIsClickingFromActionBar(true)
      if (stocksToDelete.length > 0) {
        await Promise.all(stocksToDelete.map(s => api.deleteStock(s.id)))
      }

      // Check that there is at least one stock left
      if (stocks.length < 1) {
        if (saveDraft) {
          notify.success('Brouillon sauvegardé dans la liste des offres')
        } else {
          notify.error('Veuillez renseigner au moins une date')
        }
        setIsSubmitting(false)
        return
      }
      if (stocks.length > MAX_STOCKS_PER_OFFER) {
        notify.error(
          `Veuillez créer moins de ${MAX_STOCKS_PER_OFFER} occurrences par offre.`
        )
        setIsSubmitting(false)
        return
      }

      // Upsert stocks if there are stocks to upsert
      if (stocksToCreate.length > 0) {
        const { isOk } = await upsertStocksEventAdapter({
          offerId: offer.id,
          stocks: stocksToCreate,
        })
        setIsSubmitting(false)

        if (isOk) {
          const response = await getIndividualOfferAdapter(offer.id)
          if (response.isOk) {
            const updatedOffer = response.payload
            setOffer && setOffer(updatedOffer)
          }
        } else {
          notify.error(
            "Une erreur est survenue lors de l'enregistrement de vos stocks."
          )
          return
        }
      }

      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: saveDraft
            ? OFFER_WIZARD_STEP_IDS.STOCKS
            : OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode,
        })
      )
      setIsClickingFromActionBar(false)

      if (saveDraft) {
        notify.success(getSuccessMessage(mode))
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
        icon={fullMoreIcon}
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
          fullContentWidth
        >
          <RecurrenceForm
            offer={offer}
            onCancel={onCancel}
            onConfirm={onConfirm}
          />
        </DialogBox>
      )}

      <ActionBar
        isDisabled={isOfferDisabled(offer.status) || isSubmitting}
        onClickNext={handleNextStep()}
        onClickPrevious={handlePreviousStep}
        onClickSaveDraft={handleNextStep({ saveDraft: true })}
        step={OFFER_WIZARD_STEP_IDS.STOCKS}
      />

      <RouteLeavingGuardIndividualOffer
        when={hasUnsavedStocks && !isClickingFromActionBar}
        isEdition={false}
      />
    </div>
  )
}
