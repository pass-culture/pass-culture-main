import * as Dialog from '@radix-ui/react-dialog'

import { ImageUploadBrowserForm } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/ImageUploadBrowserForm'
import { ImageUploadBrowserFormValues } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
  isReady: boolean
}

export const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
  isReady,
}: ModalImageUploadBrowserProps) => {
  return (
    <section className={style['modal-upload-browser']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>Ajouter une image</h1>
      </Dialog.Title>
      <ImageUploadBrowserForm
        isReady={isReady}
        onSubmit={onImageClientUpload}
        mode={mode}
      />
    </section>
  )
}
