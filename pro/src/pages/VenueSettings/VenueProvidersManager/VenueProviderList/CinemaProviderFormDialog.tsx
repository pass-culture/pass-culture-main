import { CinemaProviderForm } from '../CinemaProviderForm/CinemaProviderForm'

import styles from './CinemaProviderFormDialog.module.scss'

interface CinemaProviderFormDialogProps {
  onConfirm: (payload: any) => Promise<boolean>
  initialValues: any
  providerId: number
  venueId: number
  offererId: number
}

export const CinemaProviderFormDialog = ({
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
}: CinemaProviderFormDialogProps) => {
  return (
    <div className={styles['cinema-provider-form-dialog']}>
      <div className={styles['explanation']}>
        Les modifications s’appliqueront uniquement aux nouvelles offres créées.
        La modification doit être faite manuellement pour les offres existantes.
      </div>
      <CinemaProviderForm
        initialValues={initialValues}
        saveVenueProvider={onConfirm}
        providerId={providerId}
        venueId={venueId}
        offererId={offererId}
      />
    </div>
  )
}
