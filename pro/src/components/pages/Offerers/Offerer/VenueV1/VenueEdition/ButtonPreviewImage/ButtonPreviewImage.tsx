import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import DialogBox from 'new_components/DialogBox'
import Icon from 'components/layout/Icon'
import React from 'react'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'
import styles from './ButtonPreviewImage.module.scss'
import { useModal } from 'hooks/useModal'

interface IButtonPreviewImage {
  venueImage: string
}

const ButtonPreviewImage = ({
  venueImage,
}: IButtonPreviewImage): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()

  return (
    <>
      <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
        <Icon
          className={styles['image-venue-uploader-section-icon']}
          svg="ico-eye-open-filled-black"
        />
        Prévisualiser
      </Button>
      {visible && venueImage && (
        <DialogBox
          hasCloseButton
          labelledBy="Image du lieu"
          onDismiss={hideModal}
        >
          <VenueImagePreview preview={venueImage} />
        </DialogBox>
      )}
    </>
  )
}

export default ButtonPreviewImage
