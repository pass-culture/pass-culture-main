import { PropsWithChildren, useState } from 'react'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import fullMoreIcon from 'icons/full-more.svg'
import strokeAddCalendarIcon from 'icons/stroke-add-calendar.svg'
import { Button } from 'ui-kit/Button/Button'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { StocksCalendarForm } from '../StocksCalendarForm/StocksCalendarForm'

import styles from './StocksCalendarLayout.module.scss'

export function StocksCalendarLayout({
  children,
  offer,
  hasStocks,
  isLoading,
  readonly,
  onAfterCloseDialog,
}: PropsWithChildren<{
  offer: GetIndividualOfferWithAddressResponseModel
  hasStocks: boolean
  isLoading: boolean
  readonly: boolean
  onAfterCloseDialog: () => void
}>) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

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
      <StocksCalendarForm
        offer={offer}
        onAfterValidate={() => {
          onAfterCloseDialog()

          setIsDialogOpen(false)
        }}
      />
    </DialogBuilder>
  )

  return (
    <div className={styles['container']}>
      {!readonly && (
        <div className={styles['header']}>
          <h2 className={styles['title']}>Calendrier</h2>
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
