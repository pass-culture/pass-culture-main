import { useState } from 'react'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { getDepartmentCode } from 'commons/utils/getDepartmentCode'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { onSubmit } from './form/onSubmit'
import { RecurrenceFormValues } from './form/types'
import { RecurrenceForm } from './RecurrenceForm'

interface AddRecurrencesButtonProps {
  offer: GetIndividualOfferWithAddressResponseModel
  reloadStocks: () => Promise<void>
  className?: string
}

export const AddRecurrencesButton = ({
  offer,
  reloadStocks,
  className,
}: AddRecurrencesButtonProps): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)

  const handleSubmit = async (values: RecurrenceFormValues) => {
    const departmentCode = getDepartmentCode(offer)

    logEvent(Events.CLICKED_VALIDATE_ADD_RECURRENCE_DATES, {
      recurrenceType: values.recurrenceType,
      offerId: offer.id,
      venueId: offer.venue.id,
    })

    await onSubmit(values, departmentCode, offer.id, notify)
    await reloadStocks()
    setIsRecurrenceModalOpen(false)
  }

  return (
    <>
      <DialogBuilder
        onOpenChange={setIsRecurrenceModalOpen}
        open={isRecurrenceModalOpen}
        variant="drawer"
        title="Ajouter une ou plusieurs dates"
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
