import React, { useState } from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { DialogBox } from 'components/DialogBox/DialogBox'
import { useNotification } from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { onSubmit } from './form/onSubmit'
import { RecurrenceFormValues } from './form/types'
import { RecurrenceForm } from './RecurrenceForm'

interface AddRecurrencesButtonProps {
  offer: GetIndividualOfferResponseModel
  reloadStocks: () => Promise<void>
  className?: string
}

export const AddRecurrencesButton = ({
  offer,
  reloadStocks,
  className,
}: AddRecurrencesButtonProps): JSX.Element => {
  const notify = useNotification()

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const onCancel = () => setIsRecurrenceModalOpen(false)

  const handleSubmit = async (values: RecurrenceFormValues) => {
    await onSubmit(values, offer.venue.departementCode ?? '', offer.id, notify)
    await reloadStocks()
    setIsRecurrenceModalOpen(false)
  }

  return (
    <>
      <Button
        id="add-recurrence"
        variant={ButtonVariant.PRIMARY}
        onClick={() => setIsRecurrenceModalOpen(true)}
        icon={fullMoreIcon}
        className={className}
      >
        Ajouter une ou plusieurs dates
      </Button>

      {isRecurrenceModalOpen && (
        <DialogBox
          onDismiss={onCancel}
          hasCloseButton
          labelledBy="add-recurrence"
        >
          <RecurrenceForm
            priceCategories={offer.priceCategories ?? []}
            setIsOpen={setIsRecurrenceModalOpen}
            handleSubmit={handleSubmit}
            idLabelledBy="add-recurrence"
          />
        </DialogBox>
      )}
    </>
  )
}
