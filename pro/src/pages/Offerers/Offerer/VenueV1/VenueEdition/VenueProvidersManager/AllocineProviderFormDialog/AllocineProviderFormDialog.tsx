import './AllocineProviderFormDialog.scss'

import React from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import DialogBox from 'components/DialogBox/DialogBox'

import AllocineProviderForm, {
  FormValuesProps,
} from '../AllocineProviderForm/AllocineProviderForm'

interface AllocineProviderFormDialogProps {
  initialValues: FormValuesProps
  onCancel: () => void
  onConfirm: (payload: PostVenueProviderBody) => void
  providerId: number
  venueId: number
  offererId: number
}

const AllocineProviderFormDialog = ({
  onCancel,
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
}: AllocineProviderFormDialogProps) => {
  return (
    <DialogBox
      extraClassNames="allocine-provider-form-dialog"
      labelledBy="allocine-provider-form-dialog"
      onDismiss={onCancel}
    >
      <div className="title">
        <strong>Modifier les paramètres de mes offres</strong>
      </div>
      <div className="explanation">
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

export default AllocineProviderFormDialog
