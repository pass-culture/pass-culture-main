import * as Dialog from '@radix-ui/react-dialog'

import { ImageUploadBrowserForm } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/ImageUploadBrowserForm'
import { ImageUploadBrowserFormValues } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
}

export const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
}: ModalImageUploadBrowserProps) => {
  return (
    <section className={style['modal-upload-browser']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>Ajouter une image</h1>
      </Dialog.Title>
      <ImageUploadBrowserForm onSubmit={onImageClientUpload} mode={mode} />
    </section>
  )
}
