import React from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ImageUploadButton } from '../ImageUploadButton/ImageUploadButton'
import { VenueImageUploaderModal } from '../ImageVenueUploaderSection/VenueImageUploaderModal'

import styles from './ButtonEditImage.module.scss'

interface IButtonEditImage {
  venueId: string
  venueCredit?: string
  venueImage?: string
  onImageUpload: ({
    bannerUrl,
    credit,
  }: {
    bannerUrl: string
    credit: string
  }) => void
}

const ButtonEditImage = ({
  venueId,
  venueCredit,
  venueImage,
  onImageUpload,
}: IButtonEditImage): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()

  return (
    <>
      {venueImage ? (
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
          defaultImage={venueImage || undefined}
          onDismiss={hideModal}
          onImageUpload={onImageUpload}
          venueCredit={venueCredit || ''}
          venueId={venueId}
        />
      )}
    </>
  )
}

export default ButtonEditImage
