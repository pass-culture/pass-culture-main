import { useState } from 'react'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import fullMoreIcon from 'icons/full-more.svg'
import strokeAddCalendarIcon from 'icons/stroke-add-calendar.svg'
import { Button } from 'ui-kit/Button/Button'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StocksCalendar.module.scss'
import { StocksCalendarForm } from './StocksCalendarForm/StocksCalendarForm'

export function StocksCalendar({
  offer,
}: {
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  return (
    <div className={styles['container']}>
      <h2 className={styles['title']}>Calendrier</h2>
      <div className={styles['content']}>
        <div className={styles['icon-container']}>
          <SvgIcon
            alt=""
            className={styles['icon']}
            src={strokeAddCalendarIcon}
          />
        </div>
        <DialogBuilder
          trigger={
            <Button className={styles['button']} icon={fullMoreIcon}>
              Définir le calendrier
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
              setIsDialogOpen(false)
            }}
          />
        </DialogBuilder>
      </div>
    </div>
  )
}
