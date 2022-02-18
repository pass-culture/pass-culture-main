import React, { useCallback, useState, FunctionComponent } from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import DialogBox from 'new_components/DialogBox'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'
import { VenueImage } from '../VenueImage/VenueImage'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'

import styles from './ImageVenueUploaderSection.module.scss'
import { VenueImageDeleteModal } from './VenueImageDeleteModal'
import { VenueImageUploaderModal } from './VenueImageUploaderModal'

type Props = {
  venueId: string
  venueImage: string | null
  children?: never
}

export const ImageVenueUploaderSection: FunctionComponent<Props> = ({
  venueId,
  venueImage,
}) => {
  const {
    visible: isUploaderModalVisible,
    showModal: showUploaderModal,
    hideModal: hideUploaderModal,
  } = useModal()
  const {
    visible: isDeleteModalVisible,
    showModal: showDeleteModal,
    hideModal: hideDeleteModal,
  } = useModal()
  const {
    visible: isPreviewModalVisible,
    showModal: showPreviewModal,
    hideModal: hidePreviewModal,
  } = useModal()

  const [imageUniqueURL, setImageUniqueURL] = useState(venueImage)
  const reloadImage = useCallback((url: string) => {
    // URL is always the same for a venue
    // we have to reload the same URL when uploading a new one
    setImageUniqueURL(`${url}?${Math.random()}`)
  }, [])

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
      {imageUniqueURL ? (
        <div className={styles['image-venue-uploader-section-image-container']}>
          <VenueImage url={imageUniqueURL} />
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
                svg="ico-eye-open-filled"
              />
              Prévisualiser
            </Button>
            <Button onClick={showDeleteModal} variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-trash-filled"
              />
              Supprimer
            </Button>
          </div>
        </div>
      ) : (
        <ImageUploadButton onClick={showUploaderModal} />
      )}
      {!!isUploaderModalVisible && (
        <VenueImageUploaderModal
          defaultImage={imageUniqueURL || undefined}
          onDismiss={hideUploaderModal}
          reloadImage={reloadImage}
          venueId={venueId}
        />
      )}
      {!!isDeleteModalVisible && (
        <VenueImageDeleteModal onDismiss={hideDeleteModal} />
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
