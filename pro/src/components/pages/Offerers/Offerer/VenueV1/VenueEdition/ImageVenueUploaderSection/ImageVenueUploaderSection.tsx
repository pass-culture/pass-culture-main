import React from 'react'

import ButtonEditImage from '../ButtonEditImage'
import { ButtonImageDelete } from '../ButtonImageDelete'
import ButtonPreviewImage from '../ButtonPreviewImage'
import { VenueImage } from '../VenueImage/VenueImage'

import styles from './ImageVenueUploaderSection.module.scss'

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
            <ButtonEditImage
              onImageUpload={onImageUpload}
              venueCredit={venueCredit}
              venueId={venueId}
              venueImage={venueImage}
            />
            <ButtonPreviewImage venueImage={venueImage} />
            <ButtonImageDelete
              onDeleteImage={onDeleteImage}
              venueId={venueId}
            />
          </div>
        </div>
      ) : (
        <ButtonEditImage onImageUpload={onImageUpload} venueId={venueId} />
      )}
    </section>
  )
}
