import { Form, FormikProvider, useFormik } from 'formik'
import React, { useRef } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import ImageEditor, {
  ImageEditorConfig,
} from 'components/ImageEditor/ImageEditor'
import { coordonateToPosition } from 'components/ImageEditor/utils'
import { modeValidationConstraints } from 'components/ImageUploadBrowserForm/constants'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { useGetImageBitmap } from 'hooks/useGetBitmap'
import useNotification from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import { Button, Divider, SubmitButton, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ModalImageCrop.module.scss'
import { getCropMaxDimension } from './utils'

interface ModalImageCropProps {
  image: File
  credit: string
  onSetCredit: (credit: string) => void
  children?: never
  onReplaceImage: () => void
  initialPosition?: Position
  initialScale?: number
  saveInitialPosition: (position: Position) => void
  onEditedImageSave: (dataUrl: string, croppedRect: CroppedRect) => void
  mode: UploaderModeEnum
  submitButtonText: string
}

export interface ImageEditorFormValues {
  credit: string
  scale: number
}

const ModalImageCrop = ({
  onReplaceImage,
  image,
  credit,
  onSetCredit,
  onEditedImageSave,
  saveInitialPosition,
  initialPosition,
  initialScale,
  mode,
  submitButtonText,
}: ModalImageCropProps): JSX.Element => {
  const { width, height } = useGetImageBitmap(image)
  const editorRef = useRef<AvatarEditor>(null)
  const notification = useNotification()
  const minWidth = modeValidationConstraints[mode].minWidth
  // getCropMaxDimension is tested on it's own.
  /* istanbul ignore next: unable to test intercations with AvatarEditor  */
  const { width: maxWidth } = getCropMaxDimension({
    originalDimensions: { width, height },
    /* istanbul ignore next */
    orientation: mode === UploaderModeEnum.VENUE ? 'landscape' : 'portrait',
  })
  const maxScale: number = Math.min(
    4,
    (maxWidth - 10) / // Add few security pixel to garantie that max zoom will never be 399px.
      minWidth
  )
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

  /* istanbul ignore next: DEBT, TO FIX */
  const handleNext = (values: ImageEditorFormValues) => {
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
      onSetCredit(values.credit)
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    }
  }

  const initialValues = {
    credit: credit || '',
    scale: initialScale || 1,
  }

  const formik = useFormik<ImageEditorFormValues>({
    initialValues,
    onSubmit: handleNext,
  })

  return (
    <section className={style['modal-image-crop']}>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <div className={style['modal-image-crop-form']}>
            <header>
              <h1 className={style['modal-image-crop-header']}>
                Ajouter une image
              </h1>
            </header>
            <p className={style['modal-image-crop-right']}>
              En utilisant ce contenu, je certifie que je suis propriétaire ou
              que je dispose des autorisations nécessaires pour l’utilisation de
              celui-ci.
            </p>
            <ImageEditor
              {...imageEditorConfig}
              image={image}
              initialPosition={initialPosition}
              ref={editorRef}
            />
            <TextInput
              countCharacters
              className={style['modal-image-crop-credit']}
              label="Crédit de l’image"
              maxLength={255}
              name="credit"
              placeholder="Photographe..."
              required={false}
              type="text"
              isOptional
            />
          </div>
          <Divider />
          <footer className={style['modal-image-crop-footer']}>
            <Button
              icon={fullDownloadIcon}
              onClick={onReplaceImage}
              variant={ButtonVariant.TERNARY}
            >
              Remplacer l’image
            </Button>
            <SubmitButton>{submitButtonText}</SubmitButton>
          </footer>
        </Form>
      </FormikProvider>
    </section>
  )
}

export default ModalImageCrop
