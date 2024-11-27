import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash.isequal'
import { useState } from 'react'

import { api } from 'apiClient/api'
import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { pluralizeString } from 'commons/utils/pluralize'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import styles from './LinkVenuesDialog.module.scss'
import { ManadgedVenueItem } from './ManagedVenueItem/ManagedVenueItem'

interface LinkVenuesDialogProps {
  offererId: number
  selectedBankAccount: BankAccountResponseModel
  managedVenues: Array<ManagedVenues>
  closeDialog: (update?: boolean) => void
  updateBankAccountVenuePricingPoint: (venueId: number) => void
}

export const LinkVenuesDialog = ({
  offererId,
  selectedBankAccount,
  managedVenues,
  closeDialog,
  updateBankAccountVenuePricingPoint,
}: LinkVenuesDialogProps) => {
  const [showDiscardChangesDialog, setShowDiscardChangesDialog] =
    useState<boolean>(false)
  const [showUnlinkVenuesDialog, setShowUnlinkVenuesDialog] =
    useState<boolean>(false)

  const availableManagedVenuesIds = managedVenues
    .filter((venue) => !venue.bankAccountId && venue.hasPricingPoint)
    .map((venue) => venue.id)
  const notification = useNotification()
  const { logEvent } = useAnalytics()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const initialVenuesIds = selectedBankAccount.linkedVenues.map(
    (venue) => venue.id
  )
  const [selectedVenuesIds, setSelectedVenuesIds] = useState(initialVenuesIds)
  const allVenuesSelected = availableManagedVenuesIds.every(
    (venueId) => selectedVenuesIds.indexOf(venueId) >= 0
  )

  function onCancel() {
    if (isEqual(selectedVenuesIds, initialVenuesIds)) {
      closeDialog()
    } else {
      setShowDiscardChangesDialog(true)
    }
  }

  async function submitForm(hasUncheckedVenue = false) {
    if (isEqual(selectedVenuesIds, initialVenuesIds)) {
      closeDialog(false)
    } else {
      try {
        await api.linkVenueToBankAccount(offererId, selectedBankAccount.id, {
          venues_ids: selectedVenuesIds,
        })
        logEvent(BankAccountEvents.CLICKED_SAVE_VENUE_TO_BANK_ACCOUNT, {
          id: offererId,
          HasUncheckedVenue: hasUncheckedVenue,
        })
        notification.success('Vos modifications ont bien été prises en compte.')
        closeDialog(true)
        formik.setSubmitting(false)
      } catch {
        notification.error(
          'Une erreur est survenue. Vos modifications n’ont pas été prises en compte.'
        )
      }
    }
  }

  const formik = useFormik({
    initialValues: {},
    onSubmit: async () => {
      if (
        initialVenuesIds.every((venueId) => selectedVenuesIds.includes(venueId))
      ) {
        await submitForm()
      } else {
        setShowUnlinkVenuesDialog(true)
      }
    },
  })
  const hasVenuesWithoutPricingPoint = managedVenues.some(
    (venue) => !venue.hasPricingPoint
  )

  const venuesForPricingPoint = managedVenues.filter((x) => Boolean(x.siret))

  return (
    <>
      <DialogBuilder
        defaultOpen
        onOpenChange={(open) => {
          if (!open) {
            closeDialog()
          }
        }}
      >
        <div
          className={cn(styles['dialog'], {
            [styles['dialog-with-banner']]: hasVenuesWithoutPricingPoint,
          })}
        >
          <Dialog.Title asChild>
            <h1 id="bank-account" className={styles['dialog-title']}>
              Compte bancaire : {selectedBankAccount.label}
            </h1>
          </Dialog.Title>
          {hasVenuesWithoutPricingPoint && (
            <Callout
              title={
                isOfferAddressEnabled
                  ? 'Certaines de vos structures n’ont pas de SIRET'
                  : 'Certains de vos lieux n’ont pas de SIRET'
              }
              variant={CalloutVariant.ERROR}
              className={styles['dialog-callout']}
            >
              Sélectionnez un SIRET pour{' '}
              {isOfferAddressEnabled
                ? 'chacune de ces structures'
                : 'chacun de ces lieux'}{' '}
              avant de pouvoir les rattacher à ce compte bancaire.
            </Callout>
          )}
          <div className={styles['dialog-subtitle']}>
            Sélectionnez les {isOfferAddressEnabled ? 'structures' : 'lieux'}{' '}
            dont les offres seront remboursées sur ce compte bancaire.
          </div>
          <FormikProvider value={formik}>
            <form onSubmit={formik.handleSubmit}>
              <div className={styles['dialog-checkboxes']}>
                <div className={styles['dialog-select-all']}>
                  <BaseCheckbox
                    checked={allVenuesSelected || selectedVenuesIds.length >= 1}
                    partialCheck={
                      selectedVenuesIds.length >= 1 && !allVenuesSelected
                    }
                    onChange={() => {
                      if (allVenuesSelected) {
                        setSelectedVenuesIds([])
                      } else {
                        setSelectedVenuesIds([
                          ...availableManagedVenuesIds,
                          ...initialVenuesIds,
                        ])
                      }
                    }}
                    label={
                      allVenuesSelected
                        ? 'Tout désélectionner'
                        : 'Tout sélectionner'
                    }
                  />
                  <span className={styles['dialog-select-all-count']}>
                    {selectedVenuesIds.length}{' '}
                    {isOfferAddressEnabled
                      ? `${pluralizeString('structure sélectionnée', selectedVenuesIds.length)}`
                      : `${pluralizeString('lieu', selectedVenuesIds.length, 'x')} ${pluralizeString('sélectionné', selectedVenuesIds.length)}`}
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
              <div className={styles['dialog-actions']}>
                <Button variant={ButtonVariant.SECONDARY} onClick={onCancel}>
                  Annuler
                </Button>

                <Button type="submit" isLoading={formik.isSubmitting}>
                  Enregistrer
                </Button>
              </div>
            </form>
          </FormikProvider>
        </div>
      </DialogBuilder>

      <ConfirmDialog
        extraClassNames={cn(styles['discard-dialog'], {
          [styles['discard-dialog-with-banner']]: hasVenuesWithoutPricingPoint,
        })}
        icon={strokeWarningIcon}
        onCancel={() => setShowDiscardChangesDialog(false)}
        title="Les informations non sauvegardées ne seront pas prises en compte"
        onConfirm={() => {
          setShowDiscardChangesDialog(false)
          closeDialog()
        }}
        confirmText="Quitter sans enregistrer"
        cancelText="Annuler"
        open={showDiscardChangesDialog}
      />
      <ConfirmDialog
        extraClassNames={cn(styles['discard-dialog'], {
          [styles['discard-dialog-with-banner']]: hasVenuesWithoutPricingPoint,
        })}
        icon={strokeWarningIcon}
        onCancel={() => setShowUnlinkVenuesDialog(false)}
        title={
          isOfferAddressEnabled
            ? 'Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire'
            : 'Attention : le ou les lieux désélectionnés ne seront plus remboursés sur ce compte bancaire'
        }
        onConfirm={() => {
          setShowUnlinkVenuesDialog(false)
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          submitForm(true)
        }}
        confirmText="Confirmer"
        cancelText="Retour"
        open={showUnlinkVenuesDialog}
      />
    </>
  )
}
