import { useState } from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { useNotification } from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

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

  const handleSubmit = async (values: RecurrenceFormValues) => {
    await onSubmit(values, offer.venue.departementCode ?? '', offer.id, notify)
    await reloadStocks()
    setIsRecurrenceModalOpen(false)
  }

  return (
    <>
      <DialogBuilder
        onOpenChange={setIsRecurrenceModalOpen}
        open={isRecurrenceModalOpen}
        trigger={
          <Button
            variant={ButtonVariant.PRIMARY}
            icon={fullMoreIcon}
            className={className}
          >
            Ajouter une ou plusieurs dates
          </Button>
        }
      >
        <RecurrenceForm
          priceCategories={offer.priceCategories ?? []}
          handleSubmit={handleSubmit}
        />
      </DialogBuilder>
    </>
  )
}
