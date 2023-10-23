import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import DialogBox from 'components/DialogBox'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import StocksEventList from 'components/StocksEventList'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import ActionBar from '../ActionBar/ActionBar'

import { onSubmit } from './form/onSubmit'
import { RecurrenceFormValues } from './form/types'
import { HelpSection } from './HelpSection/HelpSection'
import { RecurrenceForm } from './RecurrenceForm'
import styles from './StocksEventCreation.module.scss'

export interface StocksEventCreationProps {
  offer: IndividualOffer
  stocks: StocksEvent[]
  setStocks: (stocks: StocksEvent[]) => void
}

export const StocksEventCreation = ({
  offer,
  stocks,
  setStocks,
}: StocksEventCreationProps): JSX.Element => {
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const notify = useNotification()

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const onCancel = () => setIsRecurrenceModalOpen(false)

  const handleSubmit = async (values: RecurrenceFormValues) => {
    const newStocks = await onSubmit(
      values,
      offer.venue.departementCode ?? '',
      stocks,
      offer.id,
      notify
    )
    if (newStocks?.length) {
      setStocks(newStocks)
    }
    setIsRecurrenceModalOpen(false)
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

  const handleNextStep = () => {
    // Check that there is at least one stock left
    if (stocks.length < 1) {
      notify.error('Veuillez renseigner au moins une date')
      return
    }

    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      })
    )
  }

  return (
    <div className={styles['container']}>
      {stocks.length === 0 && (
        <HelpSection className={styles['help-section']} />
      )}

      <Button
        id="add-recurrence"
        variant={ButtonVariant.PRIMARY}
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
          departmentCode={offer.venue.departementCode}
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
            priceCategories={offer.priceCategories ?? []}
            setIsOpen={setIsRecurrenceModalOpen}
            handleSubmit={handleSubmit}
          />
        </DialogBox>
      )}

      <ActionBar
        isDisabled={false}
        onClickPrevious={handlePreviousStep}
        onClickNext={handleNextStep}
        step={OFFER_WIZARD_STEP_IDS.STOCKS}
        // now we submit in RecurrenceForm, StocksEventCreation could not be dirty
        dirtyForm={false}
      />
    </div>
  )
}
