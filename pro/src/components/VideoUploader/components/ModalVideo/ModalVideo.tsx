import * as Dialog from '@radix-ui/react-dialog'
import type { JSX } from 'react'

import { TextInput } from '@/design-system/TextInput/TextInput'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'

import youtubeLogo from './assets/youtube-logo.png'
import styles from './ModalVideo.module.scss'

interface ModalVideoProps extends Omit<DialogBuilderProps, 'children'> {}

export const ModalVideo = ({
  ...dialogBuilderProps
}: ModalVideoProps): JSX.Element | null => {
  return (
    <DialogBuilder
      {...dialogBuilderProps}
      title="Ajouter une vidéo"
      imageTitle={<img alt={''} src={youtubeLogo} />}
      variant="drawer"
    >
      <div className={styles['modal-video']}>
        <div className={styles['modal-video-content']}>
          <TextInput
            name="videoUrl"
            label="Lien URL Youtube"
            description="Format : https://www.youtube.com/watch?v=0R5PZxOgoz8"
          />
        </div>
        <DialogBuilder.Footer>
          <div className={styles['modal-video-footer']}>
            <Dialog.Close asChild>
              <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
            </Dialog.Close>
            <Button type="submit">Ajouter</Button>
          </div>
        </DialogBuilder.Footer>
      </div>
    </DialogBuilder>
  )
}
