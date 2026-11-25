import { useEffect, useId, useRef, useState } from 'react'

import type { IndividualOfferImage } from '@/commons/core/Offers/types'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
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
import { buildInitialValues } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/buildInitialValues'

import styles from './IndividualOfferV2DescriptionImage.module.scss'

type IndividualOfferV2DescriptionImageProps = {
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  onImageUpload: (args: OnImageUploadArgs) => void
  onImageDelete: () => void
  isReadOnly: boolean
}

export const IndividualOfferV2DescriptionImage = ({
  displayedImage,
  onImageUpload,
  onImageDelete,
  isReadOnly,
}: IndividualOfferV2DescriptionImageProps): JSX.Element => {
  // const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()

  const uploadZoneId = useId()
  const editButtonId = useId()
  const uploadZoneRef = useRef<HTMLInputElement>(null)
  const editButtonRef = useRef<HTMLButtonElement>(null)

  const initialValues = buildInitialValues(displayedImage)
  const { croppedImageUrl, originalImageUrl, credit, alternativeText } =
    initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const [draftCredit, setDraftCredit] = useState<string | undefined>(credit)
  const [draftAlternativeText, setDraftAlternativeText] = useState<
    string | undefined
  >(alternativeText)
  const [imageError, setImageError] = useState<string | undefined>(undefined)
  // Remounting the upload zone clears its errors.
  const [uploadZoneKey, setUploadZoneKey] = useState(0)

  useEffect(() => {
    setDraftCredit(credit)
  }, [credit])
  useEffect(() => {
    setDraftAlternativeText(alternativeText)
  }, [alternativeText])

  const imageUrl = croppedImageUrl || originalImageUrl
  const hasImage = !!imageUrl
  // Once UploadZone migration is merged, uncomment these and add the imports back
  // const IMAGE_CONDITIONS_TEXT = getImageConditionsText()

  // const handleImageAdded = async (file: File) => {
  //   const { image, error } = await validateImage(file)
  //   setImageError(error)

  //   if (error) {
  //     uploadZoneRef.current?.focus({ preventScroll: true })
  //     return
  //   }

  //   logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
  //     imageType: UploaderModeEnum.OFFER,
  //     imageCreationStage: 'add image',
  //   })
  //   setDraftImage(image)
  //   setIsModalImageOpen(true)
  // }

  const onImageUploadHandler = (
    values: OnImageUploadArgs,
    successMessage: string
  ) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    setDraftCredit(values.credit ?? '')
    setDraftAlternativeText(values.alternativeText ?? '')
    onImageUpload(values)
    snackBar.success(successMessage, editButtonId)
  }

  const onImageDeleteHandler = () => {
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    onImageDelete()
    snackBar.success('L’image a bien été supprimée', uploadZoneId)
  }

  return (
    <>
      {hasImage ? (
        <div className={styles['image']}>
          <SafeImage
            alt={alternativeText || 'Prévisualisation de l’image'}
            testId="image-preview"
            className={styles['image-preview']}
            src={imageUrl}
            placeholder={
              <ImagePlaceholder className={styles['image-placeholder']} />
            }
            credit={draftCredit}
          />
          {!isReadOnly && (
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
          )}
        </div>
      ) : (
        <UploadZone
          key={uploadZoneKey}
          ref={uploadZoneRef}
          id={uploadZoneId}
          label="Ajoutez une image"
          icon={strokePictureIcon}
          // accept={ALLOWED_IMAGE_TYPES_TO_EXTENSIONS}
          // maxSize={MAX_FILE_SIZE}
          // conditionsText={IMAGE_CONDITIONS_TEXT}
          maxFiles={1}
          disabled={isReadOnly}
          error={imageError}
          // onFilesAdded={([file]) => void handleImageAdded(file)}
          // The zone displays its own errors: the one of a previous image is outdated.
          onFilesRejected={() => setImageError(undefined)}
        />
      )}
      <ModalImageUpsertOrEdit
        mode={UploaderModeEnum.OFFER}
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
    </>
  )
}
