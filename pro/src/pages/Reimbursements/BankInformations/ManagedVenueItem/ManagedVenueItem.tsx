import { useState } from 'react'

import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

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

  function handleVenueChange(event: any) {
    if (event.target.checked) {
      setSelectedVenuesIds([...selectedVenuesIds, parseInt(event.target.value)])
    } else {
      setSelectedVenuesIds(
        selectedVenuesIds.filter(
          (venueId) => venueId !== parseInt(event.target.value)
        )
      )
    }
  }

  return (
    <div className={styles['dialog-checkbox-container']}>
      <BaseCheckbox
        disabled={
          (Boolean(venue.bankAccountId) &&
            venue.bankAccountId !== selectedBankAccount.id) ||
          !venue.hasPricingPoint
        }
        label={venue.commonName}
        name={venue.id.toString()}
        value={venue.id}
        checked={selectedVenuesIds.indexOf(venue.id) >= 0}
        onChange={handleVenueChange}
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
