import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { ShareLinkButton } from '../ShareLinkButton/ShareLinkButton'
import styles from './ShareLinkDrawer.module.scss'

export const ShareLinkDrawer = () => {
  const [isOpenDialog, setIsOpenDialog] = useState(false)

  return (
    <DialogBuilder
      variant="drawer"
      onOpenChange={setIsOpenDialog}
      open={isOpenDialog}
      title="Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE"
      trigger={<ShareLinkButton />}
      className={styles['drawer']}
    >
      <div className={styles['drawer-content']}>
        Ajouter le contenu dans un autre ticket
      </div>
      <DialogBuilder.Footer>
        <Dialog.Close asChild>
          <Button variant={ButtonVariant.SECONDARY}>Fermer</Button>
        </Dialog.Close>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}
