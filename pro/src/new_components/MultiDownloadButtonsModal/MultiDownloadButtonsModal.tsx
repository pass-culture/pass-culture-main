import React, { useState } from 'react'

import { TPreFilters } from 'core/Bookings'

import { ReactComponent as DownloadSvg } from '../../icons/ico-download.svg'

import { ReactComponent as DropDownIcon } from './assets/dropdown-disclosure-down-w.svg'
import { ReactComponent as DropUpIcon } from './assets/dropdown-disclosure-up-w.svg'
import style from './MultiDownloadButtonsModal.module.scss'

interface MultiDownloadButtonsModalType {
  isDownloading: boolean
  isLocalLoading: boolean
  isFiltersDisabled: boolean
  downloadFunction: (filters: TPreFilters, type: string) => Promise<void>
  filters: TPreFilters
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
