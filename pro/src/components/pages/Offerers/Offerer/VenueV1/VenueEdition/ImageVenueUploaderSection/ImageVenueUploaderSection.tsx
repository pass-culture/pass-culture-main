import React from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import DialogBox from 'new_components/DialogBox'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ButtonImageDelete } from '../ButtonImageDelete'
import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'
import { VenueImage } from '../VenueImage/VenueImage'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'

import styles from './ImageVenueUploaderSection.module.scss'
import { VenueImageUploaderModal } from './VenueImageUploaderModal'

type ImageVenueUploaderSectionProps = {
  venueId: string
  venueImage: string | null
  venueCredit: string
  onImageUpload: ({
    bannerUrl,
    credit,
  }: {
    bannerUrl: string
    credit: string
  }) => void
  onDeleteImage: () => void
}

export const ImageVenueUploaderSection = ({
  venueId,
  venueImage,
  venueCredit,
  onImageUpload,
  onDeleteImage,
}: ImageVenueUploaderSectionProps): JSX.Element => {
  const {
    visible: isUploaderModalVisible,
    showModal: showUploaderModal,
    hideModal: hideUploaderModal,
  } = useModal()
  const {
    visible: isPreviewModalVisible,
    showModal: showPreviewModal,
    hideModal: hidePreviewModal,
  } = useModal()

  // @TODO: remove this commit with PC-13132
  const shouldDisplayImageVenueDeletion = useActiveFeature(
    'PRO_ENABLE_UPLOAD_VENUE_IMAGE'
  )

  return (
    <section
      className={
        'section vp-content-section ' + styles['image-venue-uploader-section']
      }
      data-testid="image-venue-uploader-section"
    >
      <header className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">Image du lieu</h2>
      </header>
      <p className={styles['image-venue-uploader-section-subtitle']}>
        Vous pouvez ajouter une image qui sera visible sur l'application pass
        Culture.
        <br />
        Elle permettra au public de mieux identifier votre lieu.
      </p>
      {venueImage ? (
        <div className={styles['image-venue-uploader-section-image-container']}>
          <VenueImage url={venueImage} />
          <div
            className={styles['image-venue-uploader-section-icon-container']}
          >
            <Button onClick={showUploaderModal} variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-pen-black"
              />
              Modifier
            </Button>
            <Button onClick={showPreviewModal} variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-eye-open-filled-black"
              />
              Prévisualiser
            </Button>
            {shouldDisplayImageVenueDeletion && (
              <ButtonImageDelete
                onDeleteImage={onDeleteImage}
                venueId={venueId}
              />
            )}
          </div>
        </div>
      ) : (
        <ImageUploadButton onClick={showUploaderModal} />
      )}
      {!!isUploaderModalVisible && (
        <VenueImageUploaderModal
          defaultImage={venueImage || undefined}
          onDismiss={hideUploaderModal}
          onImageUpload={onImageUpload}
          venueCredit={venueCredit}
          venueId={venueId}
        />
      )}
      {isPreviewModalVisible && venueImage && (
        <DialogBox
          hasCloseButton
          labelledBy="Image du lieu"
          onDismiss={hidePreviewModal}
        >
          <VenueImagePreview preview={venueImage} />
        </DialogBox>
      )}
    </section>
  )
}
