import React from 'react'

import { ImageUploadBrowserForm } from 'components/ImageUploadBrowserForm/ImageUploadBrowserForm'
import { ImageUploadBrowserFormValues } from 'components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
  idLabelledBy: string
}

export const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
  idLabelledBy,
}: ModalImageUploadBrowserProps) => {
  return (
    <section className={style['modal-upload-browser']}>
      <header>
        <h1 id={idLabelledBy} className={style['header']}>
          Ajouter une image
        </h1>
      </header>
      <ImageUploadBrowserForm onSubmit={onImageClientUpload} mode={mode} />
    </section>
  )
}
