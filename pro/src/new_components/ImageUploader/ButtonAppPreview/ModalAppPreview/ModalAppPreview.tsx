import React from 'react'

import DialogBox from 'new_components/DialogBox'
import { AppPreviewOffer } from 'new_components/ImageUploader/AppPreviewOffer'
import { AppPreviewVenue } from 'new_components/ImageUploader/AppPreviewVenue'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'

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
  const title = {
    [UploaderModeEnum.VENUE]: 'Image du lieu',
    [UploaderModeEnum.OFFER]: "Image de l'offre",
  }[mode]

  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
  }[mode]

  return (
    <DialogBox hasCloseButton labelledBy={title} onDismiss={hideModal}>
      <div className={style['container']}>
        <header>
          <h1 className={style['header']}>{title}</h1>
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
