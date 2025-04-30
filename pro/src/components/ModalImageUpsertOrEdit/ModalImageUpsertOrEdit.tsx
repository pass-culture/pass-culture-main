import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import AvatarEditor, { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import { useGetImageBitmap } from 'commons/hooks/useGetBitmap'
import { useNotification } from 'commons/hooks/useNotification'
import {
  UploadImageValues,
  UploaderModeEnum,
} from 'commons/utils/imageUploadTypes'
import { ImageDragAndDrop } from 'components/ImageDragAndDrop/ImageDragAndDrop'
import fullDownloadIcon from 'icons/full-download.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ImageEditor } from './components/ImageEditor/ImageEditor'
import {
  coordonateToPosition,
  widthCropPercentToScale,
} from './components/ImageEditor/utils'
import { AppPreviewOffer } from './components/ImagePreview/components/AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from './components/ImagePreview/components/AppPreviewVenue/AppPreviewVenue'
import style from './ModalImageUpsertOrEdit.module.scss'
import { getImageEditorConfig } from './utils/getImageEditorConfig'

export interface OnImageUploadArgs {
  imageFile: File
  imageCroppedDataUrl?: string
  cropParams?: CroppedRect
  credit: string | null
}

export interface ModalImageUpsertOrEditProps {
  mode: UploaderModeEnum
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete?: () => void
  initialValues?: UploadImageValues
}

export const ModalImageUpsertOrEdit = ({
  mode,
  onImageUpload,
  onImageDelete,
  initialValues = {},
}: ModalImageUpsertOrEditProps): JSX.Element | null => {
  const { draftImage, ...previouslyUploadedImage } = initialValues
  const defaultPositions = {
    x: 0.5,
    y: 0.5,
  }

  const {
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = previouslyUploadedImage
  const previouslyUploadedImageUrl = initialOriginalImageUrl

  // First version of the back don't use width_crop_percent
  // which is needed to display the original image with the correct crop.
  const {
    xCropPercent: initalXCropPercent,
    yCropPercent: initalYCropPercent,
    heightCropPercent: initalHeightCropPercent,
    widthCropPercent: initalWidthCropPercent,
  } = initialCropParams || {}
  const xInitialPosition =
    initalXCropPercent && initalWidthCropPercent
      ? coordonateToPosition(initalXCropPercent, initalWidthCropPercent)
      : defaultPositions.x
  const yInitialPosition =
    initalYCropPercent && initalHeightCropPercent
      ? coordonateToPosition(initalYCropPercent, initalHeightCropPercent)
      : defaultPositions.y

  const editorRef = useRef<AvatarEditor>(null)
  const notification = useNotification()
  const [isPaintingImage, setIsPaintingImage] = useState(true)
  const [image, setImage] = useState<File | undefined>(draftImage)
  const [previewImageUrl, setPreviewImageUrl] = useState<string | undefined>(
    previouslyUploadedImageUrl
  )
  const [editorInitialPosition, setEditorInitialPosition] = useState({
    x: xInitialPosition,
    y: yInitialPosition,
  })
  const [credit, setCredit] = useState<string>(initialCredit ?? '')
  const [scale, setScale] = useState<number>(
    initalWidthCropPercent ? widthCropPercentToScale(initalWidthCropPercent) : 1
  )

  const { width, height } = useGetImageBitmap(image)
  const imageEditorConfig = getImageEditorConfig(width, height, mode)

  const shouldDisplayWarningCallout =
    mode === UploaderModeEnum.OFFER &&
    ((width && width < 400) || (height && height < 600))

  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: () => <></>,
  }[mode]

  useEffect(() => {
    async function setImageFromUrl(url: string) {
      try {
        setImage(await getFileFromURL(url))
      } catch {
        notification.error('Erreur lors de la récupération de votre image.')
      }
    }

    if (previouslyUploadedImageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(previouslyUploadedImageUrl)
    }
  }, [previouslyUploadedImageUrl, notification])

  const onImageReplace = () => {
    setImage(undefined)
    setEditorInitialPosition({
      x: defaultPositions.x,
      y: defaultPositions.y,
    })
    setCredit('')
    setScale(1)
  }

  const onImageReplacementDropOrSelected = (file: File) => {
    setIsPaintingImage(true)
    setImage(file)
    handleImageChange()
  }

  const onEditedImageSave = (
    credit: string | null,
    imageDataUrl: string,
    croppedRect: CroppedRect
  ) => {
    if (image) {
      onImageUpload({
        imageFile: image,
        imageCroppedDataUrl: imageDataUrl,
        cropParams: croppedRect,
        credit: credit,
      })
    }
  }

  const onImagePainted = () => {
    if (editorRef.current) {
      const canvas = editorRef.current.getImage()
      setPreviewImageUrl(canvas.toDataURL())
      setIsPaintingImage(false)
    }
  }

  const handleImageChange = (
    callback?:
      | ((
          credit: string | null,
          url: string,
          cropping: AvatarEditor.CroppedRect
        ) => void)
      | undefined
  ) => {
    try {
      if (editorRef.current) {
        const canvas = editorRef.current.getImage()
        setPreviewImageUrl(canvas.toDataURL())

        const croppingRect = editorRef.current.getCroppingRect()
        setEditorInitialPosition({
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

  const onImageEditorChange = () => handleImageChange()
  const onImageSave = () => handleImageChange(onEditedImageSave)

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
        {image && (
          <>
            {isPaintingImage && <Spinner />}
            <div
              className={cn(
                style['modal-image-crop-subwrapper'],
                isPaintingImage && style['modal-image-crop-editor-loading']
              )}
            >
              <div className={style['modal-image-crop-editor']}>
                <ImageEditor
                  ref={editorRef}
                  {...imageEditorConfig}
                  image={image}
                  initialPosition={editorInitialPosition}
                  initialScale={scale}
                  onChangeDone={onImageEditorChange}
                  onImagePainted={onImagePainted}
                />
                <div className={style['modal-image-crop-actions']}>
                  <Button
                    icon={fullDownloadIcon}
                    onClick={onImageReplace}
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
              {previewImageUrl && <AppPreview imageUrl={previewImageUrl} />}
            </div>
            {shouldDisplayWarningCallout && (
              <Callout
                className={style['modal-image-crop-callout']}
                variant={CalloutVariant.WARNING}
              >
                <div>
                  La qualité de votre image n’est pas optimale.
                  <br />
                  Le format recommandé :
                  <ul className={style['modal-image-crop-callout-list']}>
                    <li>Largeur minimale de l’image : 400 px</li>
                    <li>Hauteur minimale de l’image : 600 px</li>
                  </ul>
                </div>
              </Callout>
            )}
            <TextInput
              count={credit.length}
              className={cn(
                style['modal-image-crop-credit'],
                isPaintingImage && style['modal-image-crop-credit-loading']
              )}
              label="Crédit de l’image"
              maxLength={255}
              value={credit}
              onChange={(e) => setCredit(e.target.value)}
              name="credit"
              type="text"
            />
          </>
        )}
        {!image && (
          <ImageDragAndDrop
            onDropOrSelected={onImageReplacementDropOrSelected}
            {...(mode !== UploaderModeEnum.OFFER
              ? {
                  minSizes: {
                    width: 600,
                    height: 400,
                  },
                }
              : {})}
          />
        )}
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
              onImageSave()
            }}
            disabled={!image}
          >
            Enregistrer
          </Button>
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
