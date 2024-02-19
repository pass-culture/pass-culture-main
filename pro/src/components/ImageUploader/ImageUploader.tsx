import cn from 'classnames'
import React from 'react'

import { ButtonAppPreview } from './ButtonAppPreview'
import { ButtonImageDelete } from './ButtonImageDelete'
import { ButtonImageEdit, UploadImageValues } from './ButtonImageEdit'
import { OnImageUploadArgs } from './ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { ImagePreview } from './ImagePreview'
import styles from './ImageUploader.module.scss'
import { UploaderModeEnum } from './types'

export interface ImageUploaderProps {
  className?: string
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImageAdd?: () => void
  hideActionButtons?: boolean
}

const ImageUploader = ({
  className,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  mode,
  onClickButtonImageAdd,
  hideActionButtons = false,
}: ImageUploaderProps) => {
  const { imageUrl, originalImageUrl, credit, cropParams } = initialValues

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
      {imageUrl && originalImageUrl ? (
        <>
          <ImagePreview
            mode={mode}
            imageUrl={imageUrl}
            alt="Prévisualisation de l’image"
          />
          {!hideActionButtons && (
            <div className={styles['image-uploader-actions-container']}>
              <div className={styles['actions-wrapper']}>
                <ButtonImageEdit
                  mode={mode}
                  initialValues={{
                    originalImageUrl,
                    imageUrl,
                    credit,
                    cropParams,
                  }}
                  onImageUpload={onImageUpload}
                  onClickButtonImage={onClickButtonImageAdd}
                />
                {mode !== UploaderModeEnum.OFFER_COLLECTIVE && (
                  <ButtonAppPreview imageUrl={imageUrl} mode={mode} />
                )}
                <ButtonImageDelete onImageDelete={onImageDelete} />
              </div>
            </div>
          )}
        </>
      ) : (
        <ButtonImageEdit
          mode={mode}
          onImageUpload={onImageUpload}
          onClickButtonImage={onClickButtonImageAdd}
        />
      )}
    </div>
  )
}

export default ImageUploader
