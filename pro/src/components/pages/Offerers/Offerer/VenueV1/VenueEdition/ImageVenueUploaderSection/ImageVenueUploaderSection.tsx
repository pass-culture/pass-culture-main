import React, { FunctionComponent } from 'react'

import { useModal } from 'hooks/useModal'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'

import styles from './ImageVenueUploaderSection.module.scss'
import { VenueImageUploaderModal } from './VenueImageUploaderModal'

type Props = {
  children?: never
}

export const ImageVenueUploaderSection: FunctionComponent<Props> = () => {
  const { visible, showModal, hideModal } = useModal()

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
      <ImageUploadButton onClick={showModal} />
      {!!visible && <VenueImageUploaderModal onDismiss={hideModal} />}
    </section>
  )
}
