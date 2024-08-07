import React from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import { DialogBox } from 'components/DialogBox/DialogBox'

import {
  AllocineProviderForm,
  FormValuesProps,
} from '../AllocineProviderForm/AllocineProviderForm'

import styles from './AllocineProviderFormDialog.module.scss'

interface AllocineProviderFormDialogProps {
  initialValues: FormValuesProps
  onCancel: () => void
  onConfirm: (payload: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  venueId: number
  offererId: number
}

export const AllocineProviderFormDialog = ({
  onCancel,
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
}: AllocineProviderFormDialogProps) => {
  return (
    <DialogBox
      hasCloseButton
      extraClassNames={styles['allocine-provider-form-dialog']}
      labelledBy="allocine-provider-form-dialog"
      onDismiss={onCancel}
    >
      <h1 id="allocine-provider-form-dialog" className={styles['title']}>
        <strong>Modifier les paramètres de mes offres</strong>
      </h1>
      <div className={styles['explanation']}>
        Les modifications s’appliqueront uniquement aux nouvelles offres créées.
        La modification doit être faite manuellement pour les offres existantes.
      </div>
      <AllocineProviderForm
        initialValues={initialValues}
        onCancel={onCancel}
        providerId={providerId}
        saveVenueProvider={onConfirm}
        venueId={venueId}
        offererId={offererId}
      />
    </DialogBox>
  )
}
