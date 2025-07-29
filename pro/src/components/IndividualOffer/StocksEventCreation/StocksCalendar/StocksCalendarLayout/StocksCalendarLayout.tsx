import { PropsWithChildren, useState } from 'react'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { getDepartmentCode } from 'commons/utils/getDepartmentCode'
import fullMoreIcon from 'icons/full-more.svg'
import strokeAddCalendarIcon from 'icons/stroke-add-calendar.svg'
import { Button } from 'ui-kit/Button/Button'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { onSubmit } from '../../form/onSubmit'
import { RecurrenceFormValues } from '../../form/types'
import { RecurrenceForm } from '../../RecurrenceForm'

import styles from './StocksCalendarLayout.module.scss'

export function StocksCalendarLayout({
  children,
  offer,
  hasStocks,
  isLoading,
  mode,
  onAfterCloseDialog,
}: PropsWithChildren<{
  offer: GetIndividualOfferWithAddressResponseModel
  hasStocks: boolean
  isLoading: boolean
  mode: OFFER_WIZARD_MODE
  onAfterCloseDialog: () => void
}>) {
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const handleSubmit = async (values: RecurrenceFormValues) => {
    const departmentCode = getDepartmentCode(offer)

    logEvent(Events.CLICKED_VALIDATE_ADD_RECURRENCE_DATES, {
      recurrenceType: values.recurrenceType,
      offerId: offer.id,
      venueId: offer.venue.id,
    })

    await onSubmit(values, departmentCode, offer.id, notify)
    onAfterCloseDialog()
    setIsDialogOpen(false)
  }

  const getDialogBuilderButton = (buttonLabel: string) => (
    <DialogBuilder
      trigger={
        <Button className={styles['button']} icon={fullMoreIcon}>
          {buttonLabel}
        </Button>
      }
      open={isDialogOpen}
      onOpenChange={setIsDialogOpen}
      variant="drawer"
      title="Définir le calendrier de votre offre"
    >
      <RecurrenceForm
        priceCategories={offer.priceCategories ?? []}
        handleSubmit={handleSubmit}
      />
    </DialogBuilder>
  )

  return (
    <div className={styles['container']}>
      {mode !== OFFER_WIZARD_MODE.READ_ONLY && (
        //  When the mode is read only, the title is already inside the SummarySection layout
        <div className={styles['header']}>
          <h2 className={styles['title']}>Dates et capacités</h2>
          {hasStocks &&
            getDialogBuilderButton('Ajouter une ou plusieurs dates')}
        </div>
      )}
      {isLoading && hasStocks && <Spinner className={styles['spinner']} />}
      {children}
      {!hasStocks && !isLoading && (
        <div className={styles['no-stocks-content']}>
          <div className={styles['icon-container']}>
            <SvgIcon
              alt=""
              className={styles['icon']}
              src={strokeAddCalendarIcon}
            />
          </div>
          {getDialogBuilderButton('Définir le calendrier')}
        </div>
      )}
    </div>
  )
}
