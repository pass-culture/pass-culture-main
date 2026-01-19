import cn from 'classnames'
import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import type { BankAccountResponseModel, ManagedVenue } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isEqual } from '@/commons/utils/isEqual'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import strokeWarningIcon from '@/icons/stroke-warning.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { ManadgedVenueItem } from '../ManagedVenueItem/ManagedVenueItem'
import styles from './LinkVenuesDialog.module.scss'

interface LinkVenuesDialogProps {
  offererId: number
  selectedBankAccount: BankAccountResponseModel
  managedVenues: Array<ManagedVenue>
  closeDialog: (update?: boolean) => void
  updateBankAccountVenuePricingPoint: (venueId: number) => void
  editBankAccountDialogTriggerRef?: React.RefObject<HTMLButtonElement>
}

export const LinkVenuesDialog = ({
  offererId,
  selectedBankAccount,
  managedVenues,
  closeDialog,
  updateBankAccountVenuePricingPoint,
  editBankAccountDialogTriggerRef,
}: LinkVenuesDialogProps) => {
  const [showDiscardDialog, setShowDiscardDialog] = useState<boolean>(false)
  const [showUnlinkDialog, setShowUnlinkDialog] = useState<boolean>(false)

  const availableManagedVenuesIds = managedVenues
    .filter((venue) => venue.hasPricingPoint)
    .map((venue) => venue.id)
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()

  const initialVenuesIds = selectedBankAccount.linkedVenues.map(
    (venue) => venue.id
  )

  const [selectedVenuesIds, setSelectedVenuesIds] = useState(initialVenuesIds)

  const allVenuesSelected = availableManagedVenuesIds.every((venueId) =>
    selectedVenuesIds.includes(venueId)
  )

  const saveButtonRef = useRef<HTMLButtonElement>(null)

  const handleCancel = () => {
    if (isEqual(selectedVenuesIds, initialVenuesIds)) {
      closeDialog()
    } else {
      setShowDiscardDialog(true)
    }
  }

  const handleSubmit = async (hasUnchecked = false) => {
    if (isEqual(selectedVenuesIds, initialVenuesIds)) {
      closeDialog(false)
      return
    }

    try {
      await api.linkVenueToBankAccount(offererId, selectedBankAccount.id, {
        venues_ids: selectedVenuesIds,
      })

      logEvent(BankAccountEvents.CLICKED_SAVE_VENUE_TO_BANK_ACCOUNT, {
        id: offererId,
        HasUncheckedVenue: hasUnchecked,
      })

      snackBar.success('Vos modifications ont bien été prises en compte.')
      closeDialog(true)
    } catch {
      snackBar.error(
        'Une erreur est survenue. Vos modifications n’ont pas été prises en compte'
      )
    }
  }

  const onSubmit = async () => {
    const hasUnlinked = !initialVenuesIds.every((id) =>
      selectedVenuesIds.includes(id)
    )
    hasUnlinked ? setShowUnlinkDialog(true) : await handleSubmit()
  }

  const methods = useForm({
    defaultValues: {},
  })

  const hasVenuesWithoutPricingPoint = managedVenues.some(
    (venue) => !venue.hasPricingPoint
  )

  const venuesForPricingPoint = managedVenues.filter((x) => Boolean(x.siret))

  return (
    <>
      <DialogBuilder
        defaultOpen
        variant="drawer"
        refToFocusOnClose={editBankAccountDialogTriggerRef}
        onOpenChange={(open) => {
          if (!open) {
            closeDialog()
          }
        }}
        title={`Compte bancaire : ${selectedBankAccount.label}`}
      >
        <div
          className={cn(styles['dialog'], {
            [styles['dialog-with-banner']]: hasVenuesWithoutPricingPoint,
          })}
        >
          {hasVenuesWithoutPricingPoint && (
            <div className={styles['dialog-callout']}>
              <Banner
                title="Certaines de vos structures n’ont pas de SIRET"
                variant={BannerVariants.ERROR}
                description="Sélectionnez un SIRET pour chacune de ces structures avant de pouvoir les rattacher à ce compte bancaire."
              />
            </div>
          )}
          <div className={styles['dialog-subtitle']}>
            Sélectionnez les structures dont les offres seront remboursées sur
            ce compte bancaire.
          </div>
          <form
            onSubmit={methods.handleSubmit(onSubmit)}
            className={styles['dialog-form']}
          >
            <div className={styles['dialog-checkboxes']}>
              <div className={styles['dialog-select-all']}>
                <Checkbox
                  checked={allVenuesSelected}
                  indeterminate={
                    selectedVenuesIds.length >= 1 && !allVenuesSelected
                  }
                  onChange={() => {
                    setSelectedVenuesIds(
                      allVenuesSelected
                        ? []
                        : [
                            ...new Set([
                              ...availableManagedVenuesIds,
                              ...initialVenuesIds,
                            ]),
                          ]
                    )
                  }}
                  label={
                    allVenuesSelected
                      ? 'Tout désélectionner'
                      : 'Tout sélectionner'
                  }
                />
                <span className={styles['dialog-select-all-count']}>
                  {selectedVenuesIds.length}{' '}
                  {pluralizeFr(
                    selectedVenuesIds.length,
                    'structure sélectionnée',
                    'structures sélectionnées'
                  )}
                </span>
              </div>

              {managedVenues.map((venue) => {
                return (
                  <ManadgedVenueItem
                    venue={venue}
                    key={venue.id}
                    updateBankAccountVenuePricingPoint={
                      updateBankAccountVenuePricingPoint
                    }
                    selectedBankAccount={selectedBankAccount}
                    selectedVenuesIds={selectedVenuesIds}
                    setSelectedVenuesIds={setSelectedVenuesIds}
                    venuesForPricingPoint={venuesForPricingPoint}
                  />
                )
              })}
            </div>
            <DialogBuilder.Footer>
              <div className={styles['dialog-actions']}>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  onClick={handleCancel}
                  label="Annuler"
                />

                <Button
                  type="submit"
                  isLoading={methods.formState.isSubmitting}
                  ref={saveButtonRef}
                  label="Enregistrer"
                />
              </div>
            </DialogBuilder.Footer>
          </form>
        </div>
      </DialogBuilder>

      <ConfirmDialog
        extraClassNames={cn(styles['discard-dialog'], {
          [styles['discard-dialog-with-banner']]: hasVenuesWithoutPricingPoint,
        })}
        icon={strokeWarningIcon}
        onCancel={() => setShowDiscardDialog(false)}
        title="Les informations non sauvegardées ne seront pas prises en compte"
        onConfirm={() => {
          setShowDiscardDialog(false)
          closeDialog()
        }}
        confirmText="Quitter sans enregistrer"
        cancelText="Annuler"
        open={showDiscardDialog}
        refToFocusOnClose={saveButtonRef}
      />
      <ConfirmDialog
        extraClassNames={cn(styles['discard-dialog'], {
          [styles['discard-dialog-with-banner']]: hasVenuesWithoutPricingPoint,
        })}
        icon={strokeWarningIcon}
        onCancel={() => setShowUnlinkDialog(false)}
        title="Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire"
        onConfirm={() => {
          setShowUnlinkDialog(false)
          void handleSubmit(true)
        }}
        confirmText="Confirmer"
        cancelText="Retour"
        open={showUnlinkDialog}
        refToFocusOnClose={saveButtonRef}
      />
    </>
  )
}
