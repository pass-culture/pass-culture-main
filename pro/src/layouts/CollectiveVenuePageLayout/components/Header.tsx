import { useEffect, useId, useRef, useState } from 'react'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { buildInitialVenueImageValues } from '@/commons/core/Venue/utils/buildInitialVenueImageValues'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { DisplayableActivityMap } from '@/commons/mappings/DisplayableActivity'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { WEBAPP_URL } from '@/commons/utils/config'
import {
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE,
} from '@/commons/utils/imageUpload/constants'
import {
  getImageConditionsText,
  validateImage,
} from '@/commons/utils/imageUpload/validateImage'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { ButtonImageEdit } from '@/components/ImageUploader/components/ButtonImageEdit/ButtonImageEdit'
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
import strokePictureIcon from '@/icons/stroke-picture.svg'

import styles from './Header.module.scss'

const IMAGE_CONDITIONS_TEXT = getImageConditionsText()

export interface HeaderProps {
  context: 'collective' | 'partnerPage'
}
export const Header = ({ context }: Readonly<HeaderProps>) => {
  const { logEvent } = useAnalytics()
  const { syncVenue } = useSyncVenueCache()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const snackBar = useSnackBar()

  const focusedButtonId = useId()
  const importInputId = useId()

  const { imageValues, setImageValues, handleOnImageUpload } =
    useOnVenueImageUpload(
      selectedPartnerVenue.id,
      selectedPartnerVenue.bannerUrl,
      selectedPartnerVenue.bannerMeta
    )

  const isClosed = withVenueHelpers(selectedPartnerVenue).isClosed

  const uploadZoneRef = useRef<HTMLInputElement>(null)
  const { croppedImageUrl, originalImageUrl, credit, alternativeText } =
    imageValues
  const imageUrl = croppedImageUrl || originalImageUrl
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

  const handleOnImageDelete = async () => {
    try {
      await api.deleteVenueBanner({
        path: { venue_id: selectedPartnerVenue.id },
      })
      setImageValues(buildInitialVenueImageValues(null, null))
      await syncVenue(selectedPartnerVenue.id)

      snackBar.success('Votre image a bien été supprimée', importInputId)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de la suppression de l'image",
        focusedButtonId
      )
    }
  }

  const logButtonAddClick = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  }

  const handleImageAdded = async (file: File) => {
    const { image, error } = await validateImage(file)
    setImageError(error)

    if (error) {
      uploadZoneRef.current?.focus({ preventScroll: true })
      return
    }

    logButtonAddClick()
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
      await handleOnImageUpload(values)
      snackBar.success(successMessage, focusedButtonId)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        importInputId
      )
    }
  }

  // Only deletes the image being imported: the saved one is deleted through `ButtonImageEdit`.
  const onDraftImageDelete = () => {
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    snackBar.success('L’image a bien été supprimée', importInputId)
  }

  return (
    <div className={styles['header']}>
      <div className={styles['image-uploader']}>
        {imageUrl ? (
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
        ) : (
          <UploadZone
            key={uploadZoneKey}
            ref={uploadZoneRef}
            id={importInputId}
            icon={strokePictureIcon}
            accept={ALLOWED_IMAGE_TYPES_TO_EXTENSIONS}
            maxSize={MAX_FILE_SIZE}
            conditionsText={IMAGE_CONDITIONS_TEXT}
            maxFiles={1}
            disabled={isClosed}
            error={imageError}
            onFilesAdded={([file]) => void handleImageAdded(file)}
            // The zone displays its own errors: the one of a previous image is outdated.
            onFilesRejected={() => setImageError(undefined)}
          />
        )}
        <ModalImageUpsertOrEdit
          mode={UploaderModeEnum.VENUE}
          onImageUpload={onImageUploadHandler}
          onImageDelete={onDraftImageDelete}
          initialValues={{
            ...imageValues,
            draftImage,
            credit: draftCredit,
            alternativeText: draftAlternativeText,
          }}
          refToFocusOnClose={uploadZoneRef}
          onOpenChange={(open) => {
            if (!open) {
              setUploadZoneKey((prev) => prev + 1)
            }
            setIsModalImageOpen(open)
          }}
          open={isModalImageOpen}
        />
      </div>
      <div className={styles['venue-details']}>
        <div className={styles['venue-details-main']}>
          <p className={styles['venue-type']}>
            {selectedPartnerVenue.activity &&
              DisplayableActivityMap.get(selectedPartnerVenue.activity)}
          </p>
          <h2 className={styles['venue-name']}>
            {selectedPartnerVenue.publicName}
          </h2>
        </div>

        <div className={styles['venue-details-links']}>
          {context === 'partnerPage' && !isClosed && (
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              to={`${WEBAPP_URL}/lieu/${selectedPartnerVenue.id}`}
              opensInNewTab
              label="Visualiser votre page"
            />
          )}
          {imageValues.croppedImageUrl && !isClosed && (
            <ButtonImageEdit
              mode={UploaderModeEnum.VENUE}
              initialValues={imageValues}
              onImageUpload={handleOnImageUpload}
              onImageDelete={handleOnImageDelete}
              onClickButtonImage={logButtonAddClick}
              label="Modifier l’image"
              id={focusedButtonId}
            />
          )}
        </div>
      </div>
    </div>
  )
}
