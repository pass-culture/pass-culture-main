import { useState } from 'react'

import type { BankAccountResponseModel, ManagedVenue } from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import fullEditIcon from '@/icons/full-edit.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { PricingPointDialog } from '../PricingPointDialog/PricingPointDialog'
import styles from './ManagedVenueItem.module.scss'

type ManadgedVenueItemProps = {
  venue: ManagedVenue
  updateBankAccountVenuePricingPoint: (venueId: number) => void
  selectedBankAccount: BankAccountResponseModel
  selectedVenuesIds: number[]
  setSelectedVenuesIds: (ids: number[]) => void
  venuesForPricingPoint: ManagedVenue[]
}

export function ManadgedVenueItem({
  venue,
  updateBankAccountVenuePricingPoint,
  selectedBankAccount,
  selectedVenuesIds,
  setSelectedVenuesIds,
  venuesForPricingPoint,
}: ManadgedVenueItemProps) {
  const [selectedVenue, setSelectedVenue] = useState<ManagedVenue | null>(null)
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
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullEditIcon}
              onClick={() => {
                setSelectedVenue(venue)
              }}
              className={styles['dialog-checkbox-button']}
              label="Sélectionner un SIRET"
            />
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
