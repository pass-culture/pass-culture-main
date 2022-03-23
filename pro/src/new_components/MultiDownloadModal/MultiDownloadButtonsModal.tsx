import React, { useState } from 'react'

import { ReactComponent as DownloadSvg } from '../../icons/ico-download.svg'

import { ReactComponent as DropDownIcon } from './assets/dropdown-disclosure-down-w.svg'
import { ReactComponent as DropUpIcon } from './assets/dropdown-disclosure-up-w.svg'
import style from './MultiDownloadButtonsModal.module.scss'

type DataButtonType = {
  label: string
  onClickFunction: () => void
}

type MultiDownloadButtonsModalType = {
  isDownloadingCSV: boolean
  isLocalLoading: boolean
  isFiltersDisabled: boolean
  buttonsData: [DataButtonType]
}

const MultiDownloadButtonsModal = ({
  isDownloadingCSV,
  isLocalLoading,
  isFiltersDisabled,
  buttonsData,
}: MultiDownloadButtonsModalType): JSX.Element => {
  const [isDownloadModalOptionOpen, setIsDownloadModalOptionOpen] =
    useState(false)

  return (
    <>
      <div className={style['downloadModalButton']}>
        <button
          className="primary-button"
          disabled={isDownloadingCSV || isLocalLoading || isFiltersDisabled}
          onClick={() =>
            setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
          }
          type="button"
        >
          Télécharger
          {isDownloadModalOptionOpen ? (
            <DropUpIcon className={style['dropIcon']} />
          ) : (
            <DropDownIcon className={style['dropIcon']} />
          )}
        </button>
      </div>
      {isDownloadModalOptionOpen && (
        <div className={style['downloadModalOption']}>
          {buttonsData?.map(button => (
            <button
              className={style['insideModalButton']}
              key={button.label}
              onClick={() =>
                setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
              }
              type="button"
            >
              <DownloadSvg />
              {button.label}
            </button>
          ))}
        </div>
      )}
    </>
  )
}

export default MultiDownloadButtonsModal
