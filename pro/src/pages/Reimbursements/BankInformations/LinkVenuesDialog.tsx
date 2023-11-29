import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash.isequal'
import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import DialogBox from 'components/DialogBox'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseCheckbox } from 'ui-kit/form/shared'
import { pluralize, pluralizeString } from 'utils/pluralize'

import styles from './LinkVenuesDialog.module.scss'

export interface LinkVenuesDialogProps {
  offererId: number
  selectedBankAccount: BankAccountResponseModel
  managedVenues?: Array<ManagedVenues>
  closeDialog: (update?: boolean) => void
}

const LinkVenuesDialog = ({
  offererId,
  selectedBankAccount,
  managedVenues,
  closeDialog,
}: LinkVenuesDialogProps) => {
  const [showDiscardChangesDialog, setShowDiscardChangesDialog] =
    useState<boolean>(false)
  const [showUnlinkVenuesDialog, setShowUnlinkVenuesDialog] =
    useState<boolean>(false)

  const notification = useNotification()
  const { logEvent } = useAnalytics()

  const availableManagedVenuesIds = managedVenues
    ?.filter((venue) => !venue.bankAccountId)
    ?.map((venue) => venue.id)
  const initialVenuesIds = selectedBankAccount.linkedVenues.map(
    (venue) => venue.id
  )
  const [selectedVenuesIds, setSelectedVenuesIds] = useState(
    initialVenuesIds ?? []
  )
  const allVenuesSelected = managedVenues?.every(
    (venue) => selectedVenuesIds.indexOf(venue.id) >= 0
  )

  async function submitForm(hasUncheckedVenue = false) {
    try {
      await api.linkVenueToBankAccount(offererId, selectedBankAccount.id, {
        venues_ids: selectedVenuesIds,
      })
      logEvent?.(BankAccountEvents.CLICKED_SAVE_VENUE_TO_BANK_ACCOUNT, {
        id: offererId,
        HasUncheckedVenue: hasUncheckedVenue,
      })
      notification.success('Vos modifications ont bien été prises en compte.')
      closeDialog(true)
    } catch (e) {
      notification.error(
        'Un erreur est survenue. Vos modifications n’ont pas été prises en compte.'
      )
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

  return (
    <>
      <DialogBox
        labelledBy="link-venues-dialog"
        extraClassNames={styles['dialog']}
        hasCloseButton={true}
        onDismiss={() => {
          closeDialog()
        }}
      >
        <h3 className={styles['dialog-title']}>
          Compte bancaire : {selectedBankAccount.label}
        </h3>
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
                  disabled={availableManagedVenuesIds?.length === 0}
                  onChange={() => {
                    if (allVenuesSelected) {
                      setSelectedVenuesIds(initialVenuesIds)
                    } else {
                      setSelectedVenuesIds([
                        ...(availableManagedVenuesIds ?? []),
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

              {managedVenues?.map((venue) => {
                return (
                  <BaseCheckbox
                    key={venue.id}
                    className={styles['dialog-checkbox']}
                    disabled={false} // TODO: replace with venue.hasPricingPoint
                    label={venue.commonName}
                    name={venue.id.toString()}
                    value={venue.id}
                    checked={selectedVenuesIds.indexOf(venue.id) >= 0}
                    onChange={handleVenueChange}
                  />
                )
              })}
            </div>
            <div className={styles['dialog-actions']}>
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  if (isEqual(selectedVenuesIds, initialVenuesIds)) {
                    closeDialog()
                  } else {
                    setShowDiscardChangesDialog(true)
                  }
                }}
              >
                Annuler
              </Button>
              <SubmitButton
                disabled={isEqual(selectedVenuesIds, initialVenuesIds)}
              >
                Enregistrer
              </SubmitButton>
            </div>
          </form>
        </FormikProvider>
      </DialogBox>
      {showDiscardChangesDialog && (
        <ConfirmDialog
          extraClassNames={styles['discard-dialog']}
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
    </>
  )
}

export default LinkVenuesDialog
