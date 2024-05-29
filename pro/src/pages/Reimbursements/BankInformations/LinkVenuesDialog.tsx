import cn from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { DialogBox } from 'components/DialogBox/DialogBox'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useNotification from 'hooks/useNotification'
import fullEditIcon from 'icons/full-edit.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { pluralize, pluralizeString } from 'utils/pluralize'

import styles from './LinkVenuesDialog.module.scss'
import { PricingPointDialog } from './PricingPointDialog/PricingPointDialog'

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
  const [selectedVenue, setSelectedVenue] = useState<ManagedVenues | null>(null)

  const availableManagedVenuesIds = managedVenues
    .filter((venue) => !venue.bankAccountId && venue.hasPricingPoint)
    .map((venue) => venue.id)
  const notification = useNotification()
  const { logEvent } = useAnalytics()

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
      } catch (e) {
        notification.error(
          'Un erreur est survenue. Vos modifications n’ont pas été prises en compte.'
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

  const venuesForPricingPoint = managedVenues.filter((x) => Boolean(x.siret))
  const hasVenuesWithoutPricingPoint = managedVenues.some(
    (venue) => !venue.hasPricingPoint
  )
  return (
    <>
      <DialogBox
        labelledBy="link-venues-dialog"
        extraClassNames={cn(styles['dialog'], {
          [styles['dialog-with-banner']]: hasVenuesWithoutPricingPoint,
        })}
        hasCloseButton={true}
        onDismiss={onCancel}
      >
        <h1 className={styles['dialog-title']}>
          Compte bancaire : {selectedBankAccount.label}
        </h1>
        {hasVenuesWithoutPricingPoint && (
          <Callout
            title="Certains de vos lieux n’ont pas de SIRET"
            variant={CalloutVariant.ERROR}
            className={styles['dialog-callout']}
          >
            Sélectionnez un SIRET pour chacun de ces lieux avant de pouvoir les
            rattacher à ce compte bancaire.
          </Callout>
        )}
        <div className={styles['dialog-subtitle']}>
          Sélectionnez les lieux dont les offres seront remboursées sur ce
          compte bancaire.
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
                  {`${pluralize(selectedVenuesIds.length, 'lieu', 'x')} `}
                  {pluralizeString('sélectionné', selectedVenuesIds.length)}
                </span>
              </div>

              {managedVenues.map((venue) => {
                return (
                  <div
                    key={venue.id}
                    className={styles['dialog-checkbox-container']}
                  >
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
                    )}
                  </div>
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
      </DialogBox>
      {showDiscardChangesDialog && (
        <ConfirmDialog
          extraClassNames={cn(styles['discard-dialog'], {
            [styles['discard-dialog-with-banner']]:
              hasVenuesWithoutPricingPoint,
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
        />
      )}
      {showUnlinkVenuesDialog && (
        <ConfirmDialog
          extraClassNames={cn(styles['discard-dialog'], {
            [styles['discard-dialog-with-banner']]:
              hasVenuesWithoutPricingPoint,
          })}
          icon={strokeWarningIcon}
          onCancel={() => setShowUnlinkVenuesDialog(false)}
          title="Attention : le ou les lieux désélectionnés ne seront plus remboursés sur ce compte bancaire"
          onConfirm={() => {
            setShowUnlinkVenuesDialog(false)
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            submitForm(true)
          }}
          confirmText="Confirmer"
          cancelText="Retour"
        />
      )}
      {selectedVenue && (
        <PricingPointDialog
          selectedVenue={selectedVenue}
          venues={venuesForPricingPoint}
          closeDialog={() => setSelectedVenue(null)}
          updateVenuePricingPoint={updateBankAccountVenuePricingPoint}
        />
      )}
    </>
  )
}
