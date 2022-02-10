import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import { SubmitButton } from 'ui-kit'

import style from './VenueImagePreview.module.scss'
import { VenuePreviews } from './VenuePreviews/VenuePreviews'

interface Props {
  preview: string
  onGoBack: () => void
  onUploadImage: () => void
  children?: never
  isUploading: boolean
}

export const VenueImagePreview: FunctionComponent<Props> = ({
  isUploading,
  preview,
  onGoBack,
  onUploadImage,
}) => (
  <div className={style['container']}>
    <header>
      <h1 className={style['header']}>Image du lieu</h1>
    </header>
    <div className={style['subtitle']}>
      Prévisualisation de votre image dans l’application pass Culture
    </div>
    <VenuePreviews preview={preview} />
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
        isLoading={isUploading}
        onClick={onUploadImage}
      />
    </div>
  </div>
)
