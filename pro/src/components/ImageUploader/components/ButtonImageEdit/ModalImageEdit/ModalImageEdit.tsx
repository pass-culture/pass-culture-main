import * as Dialog from '@radix-ui/react-dialog'
import { useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import {
  coordonateToPosition,
  heightCropPercentToScale,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/utils'
import { ImageUploadBrowserFormValues } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Divider } from 'ui-kit/Divider/Divider'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { AppPreviewOffer } from '../../ButtonAppPreview/components/AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from '../../ButtonAppPreview/components/AppPreviewVenue/AppPreviewVenue'
import { UploadImageValues } from '../types'

import { ModalImageCrop } from './components/ModalImageCrop/ModalImageCrop'
import { ModalImageUploadBrowser } from './components/ModalImageUploadBrowser/ModalImageUploadBrowser'
import styles from './ModalImageEdit.module.scss'

export interface OnImageUploadArgs {
  imageFile: File
  imageCroppedDataUrl?: string
  credit: string | null
  cropParams?: CroppedRect
}

interface ModalImageEditProps {
  mode: UploaderModeEnum
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete?: () => void
  initialValues?: UploadImageValues
}

// TODO: find a way to test FileReader
/* istanbul ignore next: DEBT, TO FIX */
export const ModalImageEdit = ({
  mode,
  onImageUpload,
  onImageDelete,
  initialValues = {},
}: ModalImageEditProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()

  const notification = useNotification()
  const [isReady, setIsReady] = useState<boolean>(false)

  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  const {
    imageUrl: initialImageUrl,
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = initialValues

  const [image, setImage] = useState<File | undefined>()

  const imageUrl = initialOriginalImageUrl
    ? initialOriginalImageUrl
    : initialImageUrl

  useEffect(() => {
    async function setImageFromUrl(url: string) {
      try {
        setImage(await getFileFromURL(url))
      } catch {
        notification.error('Erreur lors de la récupération de votre image.')
      }
    }

    if (imageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(imageUrl)
    }
    setIsReady(true)
  }, [])

  const [credit, setCredit] = useState(initialCredit || '')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()

  const [editedImageDataUrl, setEditedImageDataUrl] = useState(imageUrl || '')
  const [isUploading, setIsUploading] = useState(false)

  // First version of the back don't use width_crop_percent which is needed to display the original image with the correct crop
  const {
    xCropPercent: initalXCropPercent,
    yCropPercent: initalYCropPercent,
    heightCropPercent: initalHeightCropPercent,
    widthCropPercent: initalWidthCropPercent,
  } = initialCropParams || {}

  const [editorInitialPosition, setEditorInitialPosition] = useState({
    x:
      initalXCropPercent && initalWidthCropPercent
        ? coordonateToPosition(initalXCropPercent, initalWidthCropPercent)
        : 0.5,
    y:
      initalYCropPercent && initalHeightCropPercent
        ? coordonateToPosition(initalYCropPercent, initalHeightCropPercent)
        : 0.5,
  })

  const navigateFromPreviewToEdit = () => {
    setImage(undefined)
  }

  const onImageClientUpload = (values: ImageUploadBrowserFormValues) => {
    setImage(values.image || undefined)
  }

  const onReplaceImage = () => {
    setImage(undefined)
  }

  const handleImageDelete = () => {
    if (!initialImageUrl && !initialOriginalImageUrl) {
      setImage(undefined)
    } else {
      onImageDelete?.()
    }
  }

  const handleOnUpload = (
    croppedRect?: CroppedRect,
    imageToUpload?: File,
    imageDataUrl?: string
  ) => {
    if (croppedRect === undefined || imageToUpload === undefined) {
      return
    }

    logEvent(Events.CLICKED_ADD_IMAGE, {
      imageCreationStage: 'reframe image',
    })

    onImageUpload({
      imageFile: imageToUpload,
      imageCroppedDataUrl: imageDataUrl,
      cropParams: croppedRect,
      credit,
    })
    setIsUploading(false)
  }

  const showPreview = mode === UploaderModeEnum.OFFER

  const onEditedImageSave = (dataUrl: string, croppedRect: CroppedRect) => {
    setCroppingRect(croppedRect)
    setEditedImageDataUrl(dataUrl)
  }

  console.log(croppingRect, editedImageDataUrl)

  return !image ? (
    <ModalImageUploadBrowser
      onImageClientUpload={onImageClientUpload}
      mode={mode}
      isReady={isReady}
    />
  ) : (
    <>
      <Dialog.Title asChild>
        <h2 className={styles['modal-edit-title']}>Modifier une image</h2>
      </Dialog.Title>

      <p className={styles['modal-edit-description']}>
        En utilisant ce contenu, je certifie que je suis propriétaire ou que je
        dispose des autorisations nécessaires pour l’utilisation de celui-ci.
      </p>

      <form>
        <div className={styles['modal-edit-wrapper']}>
          <div>
            <ModalImageCrop
              credit={credit}
              image={image}
              initialPosition={editorInitialPosition}
              initialScale={
                initalHeightCropPercent
                  ? heightCropPercentToScale(initalHeightCropPercent)
                  : 1
              }
              onEditedImageSave={onEditedImageSave}
              onReplaceImage={onReplaceImage}
              onImageDelete={handleImageDelete}
              onSetCredit={setCredit}
              saveInitialPosition={setEditorInitialPosition}
              mode={mode}
            />
          </div>
          {showPreview && (
            <div className={styles['modal-edit-preview']}>
              <p className={styles['modal-edit-preview-description']}>
                Prévisualisation de votre image dans l’application pass Culture
              </p>
              <AppPreview imageUrl={editedImageDataUrl} />
            </div>
          )}
        </div>

        <TextInput
          count={credit.length}
          className={styles['modal-edit-credit']}
          label="Crédit image"
          maxLength={255}
          value={credit}
          onChange={(e) => setCredit(e.target.value)}
          name="credit"
          type="text"
        />

        <Divider size="large" />

        <div className={styles['modal-edit-footer']}>
          <Button
            onClick={navigateFromPreviewToEdit}
            variant={ButtonVariant.SECONDARY}
          >
            Retour
          </Button>
          <Dialog.Close asChild>
            <Button
              type="submit"
              disabled={false}
              isLoading={!!isUploading}
              onClick={() => {
                handleOnUpload(croppingRect, image, editedImageDataUrl)
              }}
            >
              Enregistrer
            </Button>
          </Dialog.Close>
        </div>
      </form>
    </>
  )
}
