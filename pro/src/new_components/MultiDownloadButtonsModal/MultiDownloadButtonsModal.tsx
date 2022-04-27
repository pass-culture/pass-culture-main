import React, { useState } from 'react'

import { ReactComponent as DownloadSvg } from '../../icons/ico-download.svg'

import { ReactComponent as DropDownIcon } from './assets/dropdown-disclosure-down-w.svg'
import { ReactComponent as DropUpIcon } from './assets/dropdown-disclosure-up-w.svg'
import style from './MultiDownloadButtonsModal.module.scss'

type MultiDownloadButtonsModalType = {
  isDownloading: boolean
  isLocalLoading: boolean
  isFiltersDisabled: boolean
  // eslint-disable-next-line
  downloadFunction: (filters: any, data: string) => void
  filters: object
}

const MultiDownloadButtonsModal = ({
  isDownloading,
  isLocalLoading,
  isFiltersDisabled,
  downloadFunction,
  filters,
}: MultiDownloadButtonsModalType): JSX.Element => {
  const [isDownloadModalOptionOpen, setIsDownloadModalOptionOpen] =
    useState(false)

  return (
    <>
      <div className={style['downloadModalButton']}>
        <button
          className="primary-button"
          disabled={isDownloading || isLocalLoading || isFiltersDisabled}
          onClick={() => {
            setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
          }}
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
      {console.log('filter', filters)}
      {isDownloadModalOptionOpen && (
        <div className={style['downloadModalOption']}>
          <button
            className={style['insideModalButton']}
            onClick={() => {
              downloadFunction(filters, 'XLS')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
            type="button"
          >
            <DownloadSvg />
            Microsoft Excel (XLS)
          </button>
          <button
            className={style['insideModalButton']}
            onClick={() => {
              downloadFunction(filters, 'CSV')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
            type="button"
          >
            <DownloadSvg />
            Fichier CSV (.CSV)
          </button>
        </div>
      )}
    </>
  )
}

export default MultiDownloadButtonsModal
