import cn from 'classnames'
import React from 'react'

import { AppPreviewOffer } from 'new_components/ImageUploader/AppPreviewOffer'
import { AppPreviewVenue } from 'new_components/ImageUploader/AppPreviewVenue'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { SubmitButton } from 'ui-kit'

import style from './ModalImageUploadConfirm.module.scss'

interface IModalImageUploadConfirmProps {
  imageUrl: string
  children?: never
  mode: UploaderModeEnum
  isUploading: boolean
  onGoBack: () => void
  onUploadImage: () => void
}

const ModalImageUploadConfirm = ({
  imageUrl,
  isUploading,
  onGoBack,
  onUploadImage,
  mode,
}: IModalImageUploadConfirmProps): JSX.Element => {
  const title = {
    [UploaderModeEnum.VENUE]: 'Image du lieu',
    [UploaderModeEnum.OFFER]: "Image de l'offre",
  }[mode]

  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
  }[mode]

  return (
    <div className={style['container']}>
      <header>
        <h1 className={style['header']}>{title}</h1>
      </header>
      <div className={style['subtitle']}>
        Prévisualisation de votre image dans l’application pass Culture
      </div>
      <AppPreview imageUrl={imageUrl} />

      <div className={style['actions']}>
        <button
          className={cn('secondary-button', style['button'])}
          onClick={onGoBack}
          title="Retour"
          type="button"
        >
          Retour
        </button>
        <SubmitButton
          className={style['button']}
          disabled={false}
          isLoading={!!isUploading}
          onClick={onUploadImage}
        />
      </div>
    </div>
  )
}

export default ModalImageUploadConfirm
