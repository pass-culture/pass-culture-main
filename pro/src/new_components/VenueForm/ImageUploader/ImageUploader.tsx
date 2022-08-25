import React, { useCallback, useState } from 'react'

import ButtonEditImage from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ButtonEditImage'
import { ButtonImageDelete } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ButtonImageDelete'
import ButtonPreviewImage from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ButtonPreviewImage'
import { VenueImage } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueImage/VenueImage'
import FormLayout from 'new_components/FormLayout'

import { IVenueFormValues } from '../types'

import styles from './ImageUploader.module.scss'

const ImageUploader = (initialValues: IVenueFormValues) => {
  const [venueUpdate, setVenueUpdate] = useState(initialValues)

  const onImageUpload = useCallback(
    ({ bannerUrl, bannerMeta }: IVenueFormValues) => {
      setVenueUpdate({
        ...initialValues,
        bannerUrl,
        bannerMeta,
      })
    },
    [initialValues]
  )
  const onDeleteImage = useCallback(() => {
    setVenueUpdate({
      ...initialValues,
      bannerUrl: undefined,
      bannerMeta: undefined,
    })
  }, [initialValues])

  return (
    <FormLayout.Section title="Image du lieu">
      <p className={styles['explanatory-text']}>
        Vous pouvez ajouter une image qui sera visible sur l’application pass
        Culture.
        <br />
        Elle permettra au public de mieux identifier votre lieu.
      </p>
      <FormLayout.Row>
        {venueUpdate.bannerUrl && venueUpdate.bannerMeta?.original_image_url ? (
          <div
            className={styles['image-venue-uploader-section-image-container']}
          >
            <VenueImage url={venueUpdate.bannerUrl} />
            <div
              className={styles['image-venue-uploader-section-icon-container']}
            >
              <ButtonEditImage
                onImageUpload={() => onImageUpload}
                venueBanner={venueUpdate.bannerMeta}
                venueId={venueUpdate.id}
                venueImage={venueUpdate.bannerUrl}
              />
              <ButtonPreviewImage venueImage={venueUpdate.bannerUrl} />
              <ButtonImageDelete
                onDeleteImage={onDeleteImage}
                venueId={venueUpdate.id}
              />
            </div>
          </div>
        ) : (
          <ButtonEditImage
            onImageUpload={() => onImageUpload}
            venueId={venueUpdate.id}
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ImageUploader
