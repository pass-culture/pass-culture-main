import { DialogBox } from 'components/DialogBox/DialogBox'

import { CinemaProviderForm } from '../CinemaProviderForm/CinemaProviderForm'

import styles from './CinemaProviderFormDialog.module.scss'

interface CinemaProviderFormDialogProps {
  onCancel: () => void
  onConfirm: (payload: any) => Promise<boolean>
  initialValues: any
  providerId: number
  venueId: number
  offererId: number
}

export const CinemaProviderFormDialog = ({
  onCancel,
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
}: CinemaProviderFormDialogProps) => {
  return (
    <DialogBox
      extraClassNames={styles['cinema-provider-form-dialog']}
      labelledBy="cinema-provider-form-dialog"
      onDismiss={onCancel}
    >
      <h1 className={styles['title']}>
        <strong>Modifier les paramètres de mes offres</strong>
      </h1>
      <div className={styles['explanation']}>
        Les modifications s’appliqueront uniquement aux nouvelles offres créées.
        La modification doit être faite manuellement pour les offres existantes.
      </div>
      <CinemaProviderForm
        initialValues={initialValues}
        onCancel={onCancel}
        saveVenueProvider={onConfirm}
        providerId={providerId}
        venueId={venueId}
        offererId={offererId}
      />
    </DialogBox>
  )
}
