import { DialogTitle } from '@radix-ui/react-dialog'
import { VisuallyHidden } from '@radix-ui/react-visually-hidden'
import { useState } from 'react'

import { Button } from '@/ui-kit/Button/Button'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import header from './assets/header.png'
import styles from './MovedBookingDownloadWarningModal.module.scss'

export const MovedBookingDownloadWarningModal = () => {
  const [isOpened, setIsOpened] = useState(false)

  return (
    <DialogBuilder
      className={styles['dialog']}
      onOpenChange={setIsOpened}
      open={isOpened}
      trigger={<Button className={styles['button']}>Télécharger</Button>}
    >
      <VisuallyHidden>
        <DialogTitle asChild>
          Modale d'alerte de déplacement du bouton de téléchargement des
          réservations
        </DialogTitle>
      </VisuallyHidden>

      <img
        className={styles['header-image']}
        src={header}
        alt=""
        aria-hidden="true"
      />
      <p className={styles['catchline']}>Nouveau !</p>
      <p>
        Retrouvez dorénavant tous vos exports de réservations dans l’onglet
        “Données d’activité” de votre Espace Administration accessible en haut à
        droite.
      </p>

      <DialogBuilder.Footer className={styles['dialog-footer']}>
        <div className={styles['form-footer']}>
          <Button onClick={() => setIsOpened(false)}>J’ai compris</Button>
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}
