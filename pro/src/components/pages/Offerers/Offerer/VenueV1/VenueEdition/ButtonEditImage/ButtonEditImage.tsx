import React from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'
import { IVenueBannerMetaProps } from '../ImageVenueUploaderSection/ImageVenueUploaderSection'
import { VenueImageUploaderModal } from '../ImageVenueUploaderSection/VenueImageUploaderModal'

import styles from './ButtonEditImage.module.scss'

interface IButtonEditImage {
  venueId: string
  venueBanner?: IVenueBannerMetaProps
  venueImage?: string
  onImageUpload: ({
    bannerUrl,
    bannerMeta,
  }: {
    bannerUrl: string
    bannerMeta: IVenueBannerMetaProps
  }) => void
}

const ButtonEditImage = ({
  venueId,
  venueBanner,
  venueImage,
  onImageUpload,
}: IButtonEditImage): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()

  return (
    <>
      {venueBanner?.original_image_url ? (
        <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
          <Icon
            alt="Modifier l'image du lieu"
            className={styles['image-venue-uploader-section-icon']}
            svg="ico-pen-black"
          />
          Modifier
        </Button>
      ) : (
        <ImageUploadButton onClick={showModal} />
      )}
      {!!visible && (
        <VenueImageUploaderModal
          onDismiss={hideModal}
          onImageUpload={onImageUpload}
          venueBanner={venueBanner}
          venueId={venueId}
          venueImage={venueImage}
        />
      )}
    </>
  )
}

export default ButtonEditImage
