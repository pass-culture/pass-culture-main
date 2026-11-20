import { useEffect, useId, useRef, useState } from 'react'

import type { BannerMetaModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events, HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { useFunctionOnce } from '@/commons/hooks/useFunctionOnce'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
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
import { Card } from '@/ui-kit/Card/Card'

import { HomepageVariant } from '../types'
import styles from './PartnerPageCard.module.scss'

const IMAGE_CONDITIONS_TEXT = getImageConditionsText()

interface PartnerPageProps {
  isReadOnly: boolean
  venueId: number
  venueName: string
  venueBannerUrl?: string | null
  venueBannerMeta?: BannerMetaModel | null
  variant: HomepageVariant
}

export const PartnerPageCard = ({
  isReadOnly,
  venueId,
  venueName,
  venueBannerUrl,
  venueBannerMeta,
  variant,
}: PartnerPageProps) => {
  const pageAccessId = useId()
  const { logEvent } = useAnalytics()
  const logPartnerPageClick = useFunctionOnce(() =>
    logEvent(HomepageEvents.CLICKED_PARTNER_PAGE)
  )
  const logFillPartnerPageClick = () =>
    logEvent(HomepageEvents.CLICKED_FILL_PARTNER_PAGE, { variant })

  const { imageValues, handleOnImageUpload } = useOnVenueImageUpload(
    venueId,
    venueBannerUrl,
    venueBannerMeta
  )
  const snackBar = useSnackBar()
  const uploadZoneId = useId()
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

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venueId}`
  const baseVenueEditionLink = `/partenaire`
  const venueEditionLink =
    variant === HomepageVariant.INDIVIDUAL
      ? `${baseVenueEditionLink}/page-partenaire`
      : `${baseVenueEditionLink}/page-collective`

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
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
      snackBar.success(successMessage)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        uploadZoneId
      )
    }
  }

  // Only deletes the image being imported: the saved one cannot be deleted from the homepage.
  const onDraftImageDelete = () => {
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    snackBar.success('L’image a bien été supprimée', uploadZoneId)
  }

  const cardTitle =
    variant === HomepageVariant.INDIVIDUAL
      ? "Votre page sur l'application"
      : 'Votre page sur ADAGE'

  return (
    <Card>
      <Card.Header title={cardTitle} />
      <Card.Content>
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
              id={uploadZoneId}
              icon={strokePictureIcon}
              accept={ALLOWED_IMAGE_TYPES_TO_EXTENSIONS}
              maxSize={MAX_FILE_SIZE}
              conditionsText={IMAGE_CONDITIONS_TEXT}
              maxFiles={1}
              disabled={isReadOnly}
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
        <h3 className={styles['venue-name']}>{venueName}</h3>
      </Card.Content>
      <Card.Footer>
        <Button
          id={pageAccessId}
          label="Compléter ma page"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          to={venueEditionLink}
          as="router-link"
          onClick={logFillPartnerPageClick}
          disabled={isReadOnly}
        />
        {variant === HomepageVariant.INDIVIDUAL && (
          <Button
            label="Voir ma page"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to={venuePreviewLink}
            as="a"
            opensInNewTab
            onClick={logPartnerPageClick}
            disabled={isReadOnly}
          />
        )}
      </Card.Footer>
    </Card>
  )
}
