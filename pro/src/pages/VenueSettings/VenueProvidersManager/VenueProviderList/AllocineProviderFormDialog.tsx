import * as Dialog from '@radix-ui/react-dialog'

import { PostVenueProviderBody } from 'apiClient/v1'

import {
  AllocineProviderForm,
  FormValuesProps,
} from '../AllocineProviderForm/AllocineProviderForm'

import styles from './AllocineProviderFormDialog.module.scss'

interface AllocineProviderFormDialogProps {
  initialValues: FormValuesProps
  onConfirm: (payload: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  venueId: number
  offererId: number
}

export const AllocineProviderFormDialog = ({
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
}: AllocineProviderFormDialogProps) => {
  return (
    <div className={styles['allocine-provider-form-dialog']}>
      <Dialog.Title asChild>
        <h1 className={styles['title']}>
          <strong>Modifier les paramètres de mes offres</strong>
        </h1>
      </Dialog.Title>
      <div className={styles['explanation']}>
        Les modifications s’appliqueront uniquement aux nouvelles offres créées.
        La modification doit être faite manuellement pour les offres existantes.
      </div>
      <AllocineProviderForm
        initialValues={initialValues}
        providerId={providerId}
        saveVenueProvider={onConfirm}
        venueId={venueId}
        offererId={offererId}
      />
    </div>
  )
}
