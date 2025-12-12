import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import type AvatarEditor from 'react-avatar-editor'
import type { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from '@/apiClient/helpers'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useGetImageBitmap } from '@/commons/hooks/useGetBitmap'
import { useNotification } from '@/commons/hooks/useNotification'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { ImageDragAndDrop } from '@/components/ImageDragAndDrop/ImageDragAndDrop'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

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

export interface ModalImageUpsertOrEditProps
  extends Omit<DialogBuilderProps, 'children'> {
  mode: UploaderModeEnum
  onImageUpload: (values: OnImageUploadArgs, successMessage: string) => void
  onImageDelete?: () => void
  initialValues?: UploadImageValues
}

export const ModalImageUpsertOrEdit = ({
  mode,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  ...dialogBuilderProps
}: ModalImageUpsertOrEditProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const { draftImage, ...previouslyUploadedImage } = initialValues
  const defaultPositions = {
    x: 0.5,
    y: 0.5,
  }

  const {
    croppedImageUrl: initialCroppedImageUrl,
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = previouslyUploadedImage

  // Only venue images seem to have both cropped and original image URLs saved.
  // Offers lose the ability to retrieve the original image URL after the first upload.
  const previouslyUploadedImageUrl =
    initialOriginalImageUrl || initialCroppedImageUrl

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
  const [isLoadingImage, setIsLoadingImage] = useState(
    !!previouslyUploadedImageUrl
  )
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
  const initialScale = initalWidthCropPercent
    ? widthCropPercentToScale(initalWidthCropPercent)
    : 1
  const [scale, setScale] = useState<number>(initialScale)

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

      setIsLoadingImage(false)
    }

    // Waiting the dialog to be opened is a minor optimization to avoid loading an image that
    // might never be displayed since the dialog is always rendered.
    if (dialogBuilderProps.open && previouslyUploadedImageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(previouslyUploadedImageUrl)
    }
  }, [dialogBuilderProps.open, previouslyUploadedImageUrl, notification])

  useEffect(() => {
    setImage(draftImage)

    if (draftImage) {
      setIsLoadingImage(false)
    }
  }, [draftImage])

  useEffect(() => {
    setCredit(initialCredit ?? '')
  }, [initialCredit])

  const hardReset = () => {
    setImage(undefined)
    setEditorInitialPosition({
      x: defaultPositions.x,
      y: defaultPositions.y,
    })
    setCredit('')
    setScale(1)
  }

  const resetWithInitialValues = () => {
    // Image needs to be kept, but
    // everything else can be reset to its initial values.
    setEditorInitialPosition({
      x: xInitialPosition,
      y: yInitialPosition,
    })
    setCredit(initialCredit ?? '')
    setScale(initialScale)
  }

  const onImageReplace = () => hardReset()

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
      logEvent(Events.CLICKED_SAVE_IMAGE, {
        imageType: mode,
        imageCreationStage: 'save',
      })

      const onlyImageHasBeenUpdated = credit === initialCredit
      onImageUpload(
        {
          imageFile: image,
          imageCroppedDataUrl: imageDataUrl,
          cropParams: croppedRect,
          credit: credit,
        },
        onlyImageHasBeenUpdated
          ? 'Votre image a bien été importée'
          : 'Vos modifications ont bien été prises en compte'
      )
    }
  }

  const onImagePainted = () => {
    if (editorRef.current) {
      const canvas = editorRef.current.getImage()
      setPreviewImageUrl(canvas.toDataURL())
      setIsPaintingImage(false)
    }
  }

  const onImageError = () => {
    setIsPaintingImage(false)
    notification.error('Erreur lors de la récupération de votre image.')
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
    <DialogBuilder
      {...dialogBuilderProps}
      onOpenChange={(open: boolean) => {
        // When dialog closes, its either :
        // - via the close button, which is a cancel action, we need a reset to inital values.
        // - externally, via dialogBuilderProps.onOpenChange, which usually
        // happens after a submit, initial values are updated so its safe to operate
        // a reset too, without a need of extra conditions.
        if (!open) {
          resetWithInitialValues()
        }

        dialogBuilderProps.onOpenChange?.(open)
      }}
      title="Modifier une image"
      variant="drawer"
    >
      <form className={style['modal-image-crop']}>
        <div className={style['modal-image-crop-content']}>
          <p className={style['modal-image-crop-right']}>
            En utilisant ce contenu, je certifie que je suis propriétaire ou que
            je dispose des autorisations nécessaires pour l’utilisation de
            celui-ci.
          </p>
          {isLoadingImage && <Spinner testId="spinner-img-load" />}
          {!isLoadingImage && image && (
            <>
              {isPaintingImage && <Spinner testId="spinner-img-paint" />}
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
                    onImageError={onImageError}
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
                <div className={style['modal-image-crop-callout']}>
                  <Banner
                    variant={BannerVariants.WARNING}
                    title="Image non conforme aux recommandations"
                    description={
                      <div>
                        Le format recommandé :
                        <ul className={style['modal-image-crop-callout-list']}>
                          <li>Largeur minimale de l’image : 400 px</li>
                          <li>Hauteur minimale de l’image : 600 px</li>
                        </ul>
                      </div>
                    }
                  />
                </div>
              )}
              <div
                className={cn(
                  style['modal-image-crop-credit'],
                  isPaintingImage && style['modal-image-crop-credit-loading']
                )}
              >
                <TextInput
                  label="Crédit de l’image"
                  name="credit"
                  maxCharactersCount={255}
                  value={credit}
                  onChange={(e) => setCredit(e.target.value)}
                />
              </div>
            </>
          )}
          {!isLoadingImage && !image && (
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
              Importer
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </DialogBuilder>
  )
}
