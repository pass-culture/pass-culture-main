import React, { FunctionComponent } from 'react'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'

import styles from './ImageVenueUploaderSection.module.scss'

type Props = {
  children?: never
}

export const ImageVenueUploaderSection: FunctionComponent<Props> = () => (
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
    <ImageUploadButton onClick={alert} />
  </section>
)
