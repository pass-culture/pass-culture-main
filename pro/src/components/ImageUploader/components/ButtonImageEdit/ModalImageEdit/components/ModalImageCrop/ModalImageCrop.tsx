import * as Dialog from '@radix-ui/react-dialog'
import { useRef, useState } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useGetImageBitmap } from 'commons/hooks/useGetBitmap'
import { useNotification } from 'commons/hooks/useNotification'
import {
  ImageEditor,
  ImageEditorConfig,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/ImageEditor'
import { coordonateToPosition } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/utils'
import { modeValidationConstraints } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/constants'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Divider } from 'ui-kit/Divider/Divider'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { getCropMaxDimension } from '../../utils/getCropMaxDimension'

import style from './ModalImageCrop.module.scss'

export type ModalImageCropProps = {
  image: File
  credit: string
  onSetCredit: (credit: string) => void
  children?: never
  onReplaceImage?: () => void
  onImageDelete: () => void
  initialPosition?: Position
  initialScale?: number
  saveInitialPosition: (position: Position) => void
  onEditedImageSave: (dataUrl: string, croppedRect: CroppedRect) => void
  mode: UploaderModeEnum
}

export const ModalImageCrop = ({
  onImageDelete,
  image,
  credit,
  onSetCredit,
  onEditedImageSave,
  saveInitialPosition,
  initialPosition,
  initialScale,
  mode,
}: ModalImageCropProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const { width, height } = useGetImageBitmap(image)
  const editorRef = useRef<AvatarEditor>(null)
  const notification = useNotification()
  const [creditInput, setCreditInput] = useState(credit || '')

  const minWidth = modeValidationConstraints[mode].minWidth

  const { width: maxWidth } = getCropMaxDimension({
    originalDimensions: { width, height },
    orientation: mode === UploaderModeEnum.VENUE ? 'landscape' : 'portrait',
  })

  const maxScale: number = Math.min(4, (maxWidth - 10) / minWidth)

  const canvasHeight: number = {
    [UploaderModeEnum.OFFER]: 384,
    [UploaderModeEnum.OFFER_COLLECTIVE]: 384,
    [UploaderModeEnum.VENUE]: 244,
  }[mode]
  const imageEditorConfig: ImageEditorConfig = {
    [UploaderModeEnum.OFFER]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 2) / 3,
      cropBorderColor: '#FFF',
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.OFFER_COLLECTIVE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 2) / 3,
      cropBorderColor: '#FFF',
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.VENUE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 3) / 2,
      cropBorderColor: '#FFF',
      cropBorderHeight: 40,
      cropBorderWidth: 100,
      maxScale,
    },
  }[mode]

  const handleNext = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      imageCreationStage: 'reframe image',
    })

    try {
      if (editorRef.current) {
        const canvas = editorRef.current.getImage()
        const croppingRect = editorRef.current.getCroppingRect()

        saveInitialPosition({
          x: coordonateToPosition(croppingRect.x, croppingRect.width),
          y: coordonateToPosition(croppingRect.y, croppingRect.height),
        })
        onEditedImageSave(canvas.toDataURL(), croppingRect)
      }
      onSetCredit(creditInput)
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    }
  }

  return (
    <section className={style['modal-image-crop']}>
      <form>
        <div>
          <Dialog.Title asChild>
            <h1 className={style['modal-image-crop-header']}>
              Modifier une image
            </h1>
          </Dialog.Title>

          <p className={style['modal-image-crop-right']}>
            En utilisant ce contenu, je certifie que je suis propriétaire ou que
            je dispose des autorisations nécessaires pour l’utilisation de
            celui-ci.
          </p>

          <div className={style['modal-image-crop-form']}>
            <div className={style['modal-image-crop-editor']}>
              <ImageEditor
                {...imageEditorConfig}
                image={image}
                initialPosition={initialPosition}
                ref={editorRef}
                initialScale={initialScale}
              />

              <div className={style['modal-image-crop-actions']}>
                <Dialog.Close asChild>
                  <Button
                    icon={fullTrashIcon}
                    onClick={onImageDelete}
                    variant={ButtonVariant.TERNARY}
                  >
                    Supprimer l’image
                  </Button>
                </Dialog.Close>
              </div>
            </div>

            <TextInput
              count={creditInput.length}
              className={style['modal-image-crop-credit']}
              label="Crédit de l’image"
              maxLength={255}
              value={creditInput}
              onChange={(e) => setCreditInput(e.target.value)}
              name="credit"
              type="text"
            />
          </div>
        </div>

        <Divider />

        <div className={style['modal-image-crop-footer']}>
          <Button
            type="submit"
            onClick={(e) => {
              e.preventDefault()
              handleNext()
            }}
          >
            Enregistrer
          </Button>
        </div>
      </form>
    </section>
  )
}
