import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import fullEditIcon from 'icons/full-edit.svg'
import { useState } from 'react'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { PricingPointDialog } from '../PricingPointDialog/PricingPointDialog'

import styles from './ManagedVenueItem.module.scss'

type ManadgedVenueItemProps = {
  venue: ManagedVenues
  updateBankAccountVenuePricingPoint: (venueId: number) => void
  selectedBankAccount: BankAccountResponseModel
  selectedVenuesIds: number[]
  setSelectedVenuesIds: (ids: number[]) => void
  venuesForPricingPoint: ManagedVenues[]
}

export function ManadgedVenueItem({
  venue,
  updateBankAccountVenuePricingPoint,
  selectedBankAccount,
  selectedVenuesIds,
  setSelectedVenuesIds,
  venuesForPricingPoint,
}: ManadgedVenueItemProps) {
  const [selectedVenue, setSelectedVenue] = useState<ManagedVenues | null>(null)
  const [isPricingPointDialogOpen, setIsPricingPointDialogOpen] =
    useState<boolean>(false)

  function handleVenueChange(
    event: React.ChangeEvent<HTMLInputElement>,
    id: number
  ) {
    if (event.target.checked) {
      setSelectedVenuesIds([...selectedVenuesIds, id])
    } else {
      setSelectedVenuesIds(
        selectedVenuesIds.filter((venueId) => venueId !== id)
      )
    }
  }

  return (
    <div className={styles['dialog-checkbox-container']}>
      <Checkbox
        disabled={
          (Boolean(venue.bankAccountId) &&
            venue.bankAccountId !== selectedBankAccount.id) ||
          !venue.hasPricingPoint
        }
        label={venue.commonName}
        name={venue.id.toString()}
        checked={selectedVenuesIds.indexOf(venue.id) >= 0}
        onChange={(e) => handleVenueChange(e, venue.id)}
      />
      {!venue.hasPricingPoint && (
        <DialogBuilder
          open={isPricingPointDialogOpen}
          onOpenChange={setIsPricingPointDialogOpen}
          variant="drawer"
          title={`Sélectionnez un SIRET pour la structure “${venue.commonName}”`}
          trigger={
            <Button
              variant={ButtonVariant.QUATERNARY}
              icon={fullEditIcon}
              iconPosition={IconPositionEnum.LEFT}
              onClick={() => {
                setSelectedVenue(venue)
              }}
              className={styles['dialog-checkbox-button']}
            >
              Sélectionner un SIRET
            </Button>
          }
        >
          <PricingPointDialog
            selectedVenue={selectedVenue}
            venues={venuesForPricingPoint}
            closeDialog={() => {
              setSelectedVenue(null)
              setIsPricingPointDialogOpen(false)
            }}
            updateVenuePricingPoint={updateBankAccountVenuePricingPoint}
          />
        </DialogBuilder>
      )}
    </div>
  )
}
