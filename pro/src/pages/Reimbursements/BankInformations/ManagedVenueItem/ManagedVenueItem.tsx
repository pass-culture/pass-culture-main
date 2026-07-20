import { useState } from 'react'

import {
  type BankAccountResponseModel,
  type ManagedVenue,
  VenueState,
} from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
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
  hasError?: boolean
}

export function ManadgedVenueItem({
  venue,
  updateBankAccountVenuePricingPoint,
  selectedBankAccount,
  selectedVenuesIds,
  setSelectedVenuesIds,
  venuesForPricingPoint,
  hasError,
}: Readonly<ManadgedVenueItemProps>) {
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
      <div className={styles['dialog-checkbox-label']}>
        <Checkbox
          disabled={
            (Boolean(venue.bankAccountId) &&
              venue.bankAccountId !== selectedBankAccount.id) ||
            !venue.hasPricingPoint
          }
          label={venue.commonName}
          name={venue.id.toString()}
          checked={selectedVenuesIds.includes(venue.id)}
          onChange={(e) => handleVenueChange(e, venue.id)}
          hasError={hasError}
        />
        {(venue.state === VenueState.CLOSED ||
          venue.state === VenueState.CLOSING) && (
          <Tag variant={TagVariant.ERROR} label="Structure fermée" />
        )}
      </div>
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
