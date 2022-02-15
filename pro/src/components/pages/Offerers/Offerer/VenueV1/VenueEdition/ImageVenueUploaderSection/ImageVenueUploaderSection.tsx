import React, { useCallback, useState, FunctionComponent } from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'
import { VenueImage } from '../VenueImage/VenueImage'

import styles from './ImageVenueUploaderSection.module.scss'
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
  const { visible, showModal, hideModal } = useModal()

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
            <Button variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-pen-black"
              />
              Modifier
            </Button>
            <Button variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-eye-open-filled"
              />
              Prévisualiser
            </Button>
            <Button variant={ButtonVariant.TERNARY}>
              <Icon
                className={styles['image-venue-uploader-section-icon']}
                svg="ico-trash-filled"
              />
              Supprimer
            </Button>
          </div>
        </div>
      ) : (
        <ImageUploadButton onClick={showModal} />
      )}
      {!!visible && (
        <VenueImageUploaderModal
          onDismiss={hideModal}
          reloadImage={reloadImage}
          venueId={venueId}
        />
      )}
    </section>
  )
}
