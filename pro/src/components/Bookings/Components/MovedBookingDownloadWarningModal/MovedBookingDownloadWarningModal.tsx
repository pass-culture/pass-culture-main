import { useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import header from './assets/header.webp'
import styles from './MovedBookingDownloadWarningModal.module.scss'

export const MovedBookingDownloadWarningModal = () => {
  const [isOpened, setIsOpened] = useState(false)

  return (
    <DialogBuilder
      className={styles['dialog']}
      isTitleHidden
      onOpenChange={setIsOpened}
      open={isOpened}
      title="Le téléchargement des réservations a déménagé"
      trigger={
        <Button
          // Warn the user this button opens a dialog
          aria-haspopup="dialog"
          label="Où les télécharger ?"
          variant={ButtonVariant.PRIMARY}
        />
      }
    >
      <img
        className={styles['header-image']}
        src={header}
        alt=""
        aria-hidden="true"
      />
      <p className={styles['catchline']}>Nouveau !</p>
      <p>
        Retrouvez dorénavant tous vos exports de réservations dans l’onglet
        “Données d’activité” de votre Espace Administration, accessible en haut
        à droite.
      </p>

      <DialogBuilder.Footer className={styles['dialog-footer']}>
        <div className={styles['form-footer']}>
          <Button
            as="a"
            label="Aller sur la nouvelle page de téléchargement"
            onClick={() => setIsOpened(false)}
            to="/remboursements"
            variant={ButtonVariant.PRIMARY}
          />
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}
