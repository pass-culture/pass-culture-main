import * as Dialog from '@radix-ui/react-dialog'
import { useRef, useState } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useGetImageBitmap } from 'commons/hooks/useGetBitmap'
import { useNotification } from 'commons/hooks/useNotification'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import fullDownloadIcon from 'icons/full-download.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { getCropMaxDimension } from '../../utils/getCropMaxDimension'
import { modeValidationConstraints } from '../ModalImageUploadBrowser/ImageUploadBrowserForm/constants'

import { ImageEditor, ImageEditorConfig } from './ImageEditor/ImageEditor'
import { coordonateToPosition } from './ImageEditor/utils'
import style from './ModalImageCrop.module.scss'

export type ModalImageCropProps = {
  image: File
  initialCredit?: string | null
  children?: never
  onReplaceImage: () => void
  onImageDelete: () => void
  initialPosition?: Position
  initialScale?: number
  saveInitialPosition: (position: Position) => void
  onEditedImageSave: (
    credit: string | null,
    dataUrl: string,
    croppedRect: CroppedRect
  ) => void
  mode: UploaderModeEnum
  imageUrl?: string
}

export const ModalImageCrop = ({
  image,
  initialCredit,
  onReplaceImage,
  onImageDelete,
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
  const [credit, setCredit] = useState(initialCredit || '')

  const minWidth = modeValidationConstraints[mode].minWidth

  const { width: maxWidth } = getCropMaxDimension({
    originalDimensions: { width, height },
    orientation: mode === UploaderModeEnum.VENUE ? 'landscape' : 'portrait',
  })

  const AppPreview = {
    [UploaderModeEnum.VENUE]: () => <></>,
    [UploaderModeEnum.OFFER]: () => <></>,
    [UploaderModeEnum.OFFER_COLLECTIVE]: () => <></>,
  }[mode]

  const maxScale: number = Math.min(4, (maxWidth - 10) / minWidth)

  const canvasHeight: number = {
    [UploaderModeEnum.OFFER]: 297,
    [UploaderModeEnum.OFFER_COLLECTIVE]: 297,
    [UploaderModeEnum.VENUE]: 138,
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

  const handleImageChange = (
    callback?:
      | ((
          credit: string | null,
          url: string,
          cropping: AvatarEditor.CroppedRect
        ) => void)
      | undefined
  ) => {
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

        if (callback) {
          callback(credit, canvas.toDataURL(), croppingRect)
        }
      }
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    }
  }

  function handleSave() {
    return handleImageChange(onEditedImageSave)
  }

  const handleChangeDone = () => {
    return handleImageChange()
  }

  return (
    <form className={style['modal-image-crop']}>
      <div className={style['modal-image-crop-content']}>
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

        <div className={style['modal-image-crop-wrapper']}>
          <div className={style['modal-image-crop-editor']}>
            <ImageEditor
              {...imageEditorConfig}
              image={image}
              initialPosition={initialPosition}
              ref={editorRef}
              initialScale={initialScale}
              onChangeDone={handleChangeDone}
            />
            <div className={style['modal-image-crop-actions']}>
              <Button
                icon={fullDownloadIcon}
                onClick={onReplaceImage}
                variant={ButtonVariant.TERNARY}
              >
                Remplacer l’image
              </Button>

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
          <AppPreview />
        </div>

        <TextInput
          count={credit.length}
          className={style['modal-image-crop-credit']}
          label="Crédit de l’image"
          maxLength={255}
          value={credit}
          onChange={(e) => setCredit(e.target.value)}
          name="credit"
          type="text"
        />
      </div>

      <DialogBuilder.Footer>
        <div className={style['modal-image-crop-footer']}>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Button
            type="submit"
            onClick={(e) => {
              e.preventDefault()
              handleSave()
            }}
          >
            Enregistrer
          </Button>
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
