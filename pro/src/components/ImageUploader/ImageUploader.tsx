import cn from 'classnames'

import {
  UploadImageValues,
  UploaderModeEnum,
} from 'commons/utils/imageUploadTypes'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ImagePlaceholder } from 'components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from 'components/SafeImage/SafeImage'

import { ButtonImageDelete } from './components/ButtonImageDelete/ButtonImageDelete'
import { ButtonImageEdit } from './components/ButtonImageEdit/ButtonImageEdit'
import styles from './ImageUploader.module.scss'

export interface ImageUploaderProps {
  className?: string
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  onClickButtonImageAdd?: () => void
  hideActionButtons?: boolean
  disableForm?: boolean
}

export const ImageUploader = ({
  className,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  onClickButtonImageAdd,
  hideActionButtons = false,
  disableForm = false,
}: ImageUploaderProps) => {
  const { imageUrl, originalImageUrl, credit, cropParams } = initialValues

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
      {imageUrl && originalImageUrl ? (
        <>
          <SafeImage
            alt={'Prévisualisation de l’image'}
            data-testid="image-preview"
            className={cn(styles['image-preview'], styles['preview-venue'])}
            src={imageUrl}
            placeholder={
              <ImagePlaceholder className={styles['placeholder-venue']} />
            }
          />
          {!hideActionButtons && (
            <div className={styles['image-uploader-actions-container']}>
              <div className={styles['actions-wrapper']}>
                <ButtonImageEdit
                  mode={UploaderModeEnum.VENUE}
                  initialValues={{
                    originalImageUrl,
                    imageUrl,
                    credit,
                    cropParams,
                  }}
                  onImageUpload={onImageUpload}
                  onImageDelete={onImageDelete}
                  onClickButtonImage={onClickButtonImageAdd}
                  disableForm={disableForm}
                />

                <ButtonImageDelete onImageDelete={onImageDelete} />
              </div>
            </div>
          )}
        </>
      ) : (
        <ButtonImageEdit
          mode={UploaderModeEnum.VENUE}
          onImageUpload={onImageUpload}
          onImageDelete={onImageDelete}
          onClickButtonImage={onClickButtonImageAdd}
          disableForm={disableForm}
        />
      )}
    </div>
  )
}
