import React from 'react'

import DialogBox from 'components/DialogBox'
import { AppPreviewOffer } from 'components/ImageUploader/AppPreviewOffer'
import { AppPreviewVenue } from 'components/ImageUploader/AppPreviewVenue'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import style from './ModalAppPreview.module.scss'

interface IModalAppPreviewProps {
  hideModal: () => void
  mode: UploaderModeEnum
  imageUrl: string
  children?: never
}

const ModalAppPreview = ({
  mode,
  hideModal,
  imageUrl,
}: IModalAppPreviewProps): JSX.Element => {
  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <DialogBox
      hasCloseButton
      labelledBy="Ajouter une image"
      onDismiss={hideModal}
    >
      <div className={style['container']}>
        <header>
          <h1 className={style['header']}>Ajouter une image</h1>
        </header>
        <div className={style['subtitle']}>
          Prévisualisation de votre image dans l’application pass Culture
        </div>
        <AppPreview imageUrl={imageUrl} />
      </div>
    </DialogBox>
  )
}

export default ModalAppPreview
