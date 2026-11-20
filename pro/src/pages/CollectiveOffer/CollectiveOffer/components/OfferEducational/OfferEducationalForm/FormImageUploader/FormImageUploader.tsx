import { useEffect, useId, useRef, useState } from 'react'

import type { OfferCollectiveImage } from '@/commons/core/Offers/types'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE,
  MIN_COLLECTIVE_IMAGE_DIMENSIONS,
} from '@/commons/utils/imageUpload/constants'
import {
  getImageConditionsText,
  validateImage,
} from '@/commons/utils/imageUpload/validateImage'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import {
  ModalImageUpsertOrEdit,
  type OnImageUploadArgs,
} from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { UploadZone } from '@/design-system/UploadZone/UploadZone'
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokePictureIcon from '@/icons/stroke-picture.svg'

import styles from './FormImageUploader.module.scss'

const IMAGE_CONDITIONS_TEXT = getImageConditionsText(
  MIN_COLLECTIVE_IMAGE_DIMENSIONS
)

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  onImageDropOrSelected?: () => void
  imageOffer: OfferCollectiveImage | null
  disableForm: boolean
  isTemplate: boolean
}

const buildInitialValues = (
  imageOffer: OfferCollectiveImage | null
): UploadImageValues => ({
  croppedImageUrl: imageOffer?.url || '',
  credit: imageOffer?.credit || '',
  alternativeText: imageOffer?.alternativeText || '',
})

export const FormImageUploader = ({
  onImageUpload,
  onImageDelete,
  onImageDropOrSelected,
  imageOffer,
  disableForm,
  isTemplate,
}: ImageUploaderOfferProps) => {
  const snackBar = useSnackBar()
  const uploadZoneId = useId()
  const editButtonId = useId()
  const uploadZoneRef = useRef<HTMLInputElement>(null)
  const editButtonRef = useRef<HTMLButtonElement>(null)

  const initialValues = buildInitialValues(imageOffer)
  const { croppedImageUrl, credit, alternativeText } = initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const [draftCredit, setDraftCredit] = useState<string | undefined>(credit)
  const [draftAlternativeText, setDraftAlternativeText] = useState<
    string | undefined
  >(alternativeText)
  const [imageError, setImageError] = useState<string | undefined>(undefined)
  // Remounting the upload zone clears its errors.
  const [uploadZoneKey, setUploadZoneKey] = useState(0)

  const hasImage = !!croppedImageUrl

  useEffect(() => {
    setDraftCredit(credit)
  }, [credit])
  useEffect(() => {
    setDraftAlternativeText(alternativeText)
  }, [alternativeText])

  const handleImageAdded = async (file: File) => {
    const { image, error } = await validateImage(
      file,
      MIN_COLLECTIVE_IMAGE_DIMENSIONS
    )
    setImageError(error)

    if (error) {
      uploadZoneRef.current?.focus({ preventScroll: true })
      return
    }

    onImageDropOrSelected?.()
    setDraftImage(image)
    setIsModalImageOpen(true)
  }

  const onImageUploadHandler = async (
    values: OnImageUploadArgs,
    successMessage: string
  ) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    setDraftCredit(values.credit ?? '')
    setDraftAlternativeText(values.alternativeText ?? '')
    try {
      await Promise.resolve(onImageUpload(values))
      snackBar.success(successMessage, editButtonId)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        uploadZoneId
      )
    }
  }

  const onImageDeleteHandler = () => {
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    onImageDelete()
    snackBar.success('L’image a bien été supprimée', uploadZoneId)
  }

  return (
    <FormLayout.Section
      title="Illustrez votre offre"
      description={
        isTemplate
          ? 'Ajoutez une image pour que votre offre ait 2 fois plus de chances d’être consultée !'
          : ''
      }
    >
      <FormLayout.Row>
        {hasImage ? (
          <div className={styles['image']}>
            <SafeImage
              alt={alternativeText || 'Prévisualisation de l’image'}
              testId="image-preview"
              className={styles['image-preview']}
              src={croppedImageUrl}
              placeholder={
                <ImagePlaceholder className={styles['image-placeholder']} />
              }
              credit={draftCredit}
            />
            <div className={styles['image-actions']}>
              <Button
                ref={editButtonRef}
                onClick={() => setIsModalImageOpen(true)}
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                size={ButtonSize.SMALL}
                aria-label="Modifier l’image"
                icon={fullEditIcon}
                label="Modifier"
                id={editButtonId}
              />
              <Button
                onClick={onImageDeleteHandler}
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                size={ButtonSize.SMALL}
                icon={fullTrashIcon}
                label="Supprimer"
              />
            </div>
          </div>
        ) : (
          <UploadZone
            key={uploadZoneKey}
            ref={uploadZoneRef}
            id={uploadZoneId}
            icon={strokePictureIcon}
            accept={ALLOWED_IMAGE_TYPES_TO_EXTENSIONS}
            maxSize={MAX_FILE_SIZE}
            conditionsText={IMAGE_CONDITIONS_TEXT}
            maxFiles={1}
            disabled={disableForm}
            error={imageError}
            onFilesAdded={([file]) => void handleImageAdded(file)}
            // The zone displays its own errors: the one of a previous image is outdated.
            onFilesRejected={() => setImageError(undefined)}
          />
        )}
        <ModalImageUpsertOrEdit
          mode={UploaderModeEnum.OFFER_COLLECTIVE}
          onImageUpload={onImageUploadHandler}
          onImageDelete={onImageDeleteHandler}
          initialValues={{
            ...initialValues,
            draftImage,
            credit: draftCredit,
            alternativeText: draftAlternativeText,
          }}
          refToFocusOnClose={hasImage ? editButtonRef : uploadZoneRef}
          onOpenChange={(open) => {
            if (!open) {
              setUploadZoneKey((prev) => prev + 1)
            }
            setIsModalImageOpen(open)
          }}
          open={isModalImageOpen}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
