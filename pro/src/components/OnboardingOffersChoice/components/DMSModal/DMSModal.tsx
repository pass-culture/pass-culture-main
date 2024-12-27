import cn from 'classnames'

import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import acceptationIcon from './assets/acceptation.svg'
import calendarIcon from './assets/calendrier.svg'
import offerCreationIcon from './assets/creation_offre.svg'
import fileSubmissionIcon from './assets/depot_dossier.svg'
import styles from './DMSModal.module.scss'

interface DMSModalProps {
  className?: string
}

export const DMSModal = ({ className }: DMSModalProps): JSX.Element => {
  return (
    <div className={cn(styles[`dms-modal`], className)}>
      <h1 className={styles['dms-title']}>Quelles sont les étapes ?</h1>
      <p className={styles['dms-text']}>
        Pour continuer, vous devez compléter un dossier qui sera examiné par les
        services d’État pour vérifier votre éligibilité au dispositif pass
        Culture.
      </p>
      <div className={styles['dms-steps']}>
        <DMSStep
          icon={fileSubmissionIcon}
          text="Dépôt du dossier de présentation de votre structure"
        />
        <DMSStep
          icon={acceptationIcon}
          text="Étude et validation du dossier en commission de votre territoire"
        />
        <DMSStep
          icon={offerCreationIcon}
          text="Création de vos offres sur le pass Culture Pro"
        />
        <DMSStep
          icon={calendarIcon}
          text="Réservation de vos offres par les enseignants sur ADAGE"
        />
      </div>
      <div className={styles['dms-actions']}>
        <Button className={styles['dms-button']} icon={fullLinkIcon}>
          Déposer un dossier
        </Button>
        <Button
          className={styles['dms-button']}
          variant={ButtonVariant.TERNARY}
          icon={fullNextIcon}
        >
          J’ai déposé un dossier
        </Button>
      </div>
      <div className={styles['error-message']}>
        Un problème est survenu, veuillez réessayer
      </div>
    </div>
  )
}

function DMSStep({ icon, text }: { icon: string; text: string }) {
  return (
    <div className={styles['dms-step']}>
      <img src={icon} alt="" className={styles['dms-step-icon']} />
      <p className={styles['dms-step-text']}>{text}</p>
    </div>
  )
}
