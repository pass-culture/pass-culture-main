import * as Dialog from '@radix-ui/react-dialog'
import { useEffect, useRef } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import { useGetImageBitmap } from 'commons/hooks/useGetBitmap'
import {
  ImageEditor,
  ImageEditorConfig,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/ImageEditor'
import { coordonateToPosition } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/utils'
import { modeValidationConstraints } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/constants'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import fullDownloadIcon from 'icons/full-download.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { getCropMaxDimension } from '../../utils/getCropMaxDimension'

import style from './ModalImageCrop.module.scss'

export type ModalImageCropProps = {
  image: File
  credit: string
  onSetCredit: (credit: string) => void
  children?: never
  onReplaceImage: () => void
  onImageDelete: () => void
  initialPosition?: Position
  initialScale?: number
  saveInitialPosition: (position: Position) => void
  onEditedImageSave: (dataUrl: string, croppedRect: CroppedRect) => void
  mode: UploaderModeEnum
}

export const ModalImageCrop = ({
  onReplaceImage,
  onImageDelete,
  image,
  onEditedImageSave,
  saveInitialPosition,
  initialPosition,
  initialScale,
  mode,
}: ModalImageCropProps): JSX.Element => {
  const { width, height } = useGetImageBitmap(image)
  const editorRef = useRef<AvatarEditor>(null)

  const minWidth = modeValidationConstraints[mode].minWidth

  const { width: maxWidth } = getCropMaxDimension({
    originalDimensions: { width, height },
    orientation: mode === UploaderModeEnum.VENUE ? 'landscape' : 'portrait',
  })

  const maxScale: number = Math.min(4, (maxWidth - 10) / minWidth)

  const canvasHeight: number = {
    [UploaderModeEnum.OFFER]: 300,
    [UploaderModeEnum.OFFER_COLLECTIVE]: 300,
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

  const onImageChange = () => {
    try {
      if (editorRef.current) {
        const canvas = editorRef.current.getImage()
        const croppingRect = editorRef.current.getCroppingRect()

        saveInitialPosition({
          x: coordonateToPosition(croppingRect.x, croppingRect.width),
          y: coordonateToPosition(croppingRect.y, croppingRect.height),
        })

        const debounced = setTimeout(() => {
          onEditedImageSave(canvas.toDataURL(), croppingRect)
        }, 1000)
        return () => clearTimeout(debounced)
      }
    } catch {
      /* empty */
    }
    return
  }

  return (
    <section className={style['modal-image-crop']}>
      <div className={style['modal-image-crop-form']}>
        <div className={style['modal-image-crop-editor']}>
          <ImageEditor
            {...imageEditorConfig}
            image={image}
            initialPosition={initialPosition}
            ref={editorRef}
            initialScale={initialScale}
            onImageChange={onImageChange}
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
      </div>
    </section>
  )
}
