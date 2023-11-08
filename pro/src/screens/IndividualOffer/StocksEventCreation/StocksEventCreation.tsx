import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import DialogBox from 'components/DialogBox'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import StocksEventList from 'components/StocksEventList'
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
}

export const StocksEventCreation = ({
  offer,
}: StocksEventCreationProps): JSX.Element => {
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const notify = useNotification()

  const [hasStocks, setHasStocks] = useState<boolean | null>(null)
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)

  const handleSubmit = async (values: RecurrenceFormValues) => {
    await onSubmit(values, offer.venue.departementCode ?? '', offer.id, notify)
    setIsRecurrenceModalOpen(false)
    setHasStocks(true)
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
    if (!hasStocks) {
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
      {hasStocks === false && (
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

      {hasStocks !== false && (
        <StocksEventList
          className={styles['stock-section']}
          priceCategories={offer.priceCategories ?? []}
          departmentCode={offer.venue.departementCode}
          offerId={offer.id}
          onStocksLoad={setHasStocks}
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
