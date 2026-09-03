import { Checkbox } from '@/design-system/Checkbox/Checkbox'

import styles from '../CloseVenueModal.module.scss'

type CloseVenueCardProps = {
  name: string
  siret: string | null
  certified: boolean
  onCertify: (certified: boolean) => void
}

export const CloseVenueCard = ({
  name,
  siret,
  certified,
  onCertify,
}: CloseVenueCardProps): JSX.Element => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-container']}>
        <h3 className={styles['modal-content-subtitle']}>
          Structure concernée :
        </h3>
        <p className={styles['card-name']}>
          {name} - SIRET : {siret ?? 'Aucun SIRET'}
        </p>
        <Checkbox
          required
          onChange={(e) => onCertify(e.target.checked)}
          label="Je certifie être habilité(e) à demander la fermeture de la structure et à avoir pris connaissance des impacts que cela entraine."
          checked={certified}
        />
      </div>
    </div>
  )
}
