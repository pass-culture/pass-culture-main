import fullShowIcon from 'icons/full-show.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { UploaderModeEnum } from '../types'

import { ModalAppPreview } from './ModalAppPreview'

export interface ButtonAppPreviewProps {
  mode: UploaderModeEnum
  imageUrl: string
}

export const ButtonAppPreview = ({
  imageUrl,
  mode,
}: ButtonAppPreviewProps): JSX.Element => {
  return (
    <>
      <DialogBuilder
        trigger={
          <Button variant={ButtonVariant.TERNARY} icon={fullShowIcon}>
            Prévisualiser
          </Button>
        }
      >
        {imageUrl && <ModalAppPreview mode={mode} imageUrl={imageUrl} />}
      </DialogBuilder>
    </>
  )
}
