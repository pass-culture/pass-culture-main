import React from 'react'

import style from './ImportFromComputerInput.module.scss'

export type IImportFromComputerInputProps = {
  imageTypes: string[]
  isValid: boolean
  onSetImage: React.ChangeEventHandler<HTMLInputElement>
  children?: never
}

export const ImportFromComputerInput = ({
  isValid,
  imageTypes,
  onSetImage,
}: IImportFromComputerInputProps): JSX.Element => (
  <label className={'primary-link ' + style['import-from-computer-input']}>
    Importer une image depuis l’ordinateur
    <input
      accept={imageTypes.join()}
      aria-invalid={isValid}
      className={style['import-from-computer-input-file-input']}
      onChange={onSetImage}
      type="file"
    />
  </label>
)
