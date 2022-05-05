import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import useOnClickOrFocusOutside from 'components/hooks/useOnClickOrFocusOutside'
import { TPreFilters } from 'core/Bookings'
import { Events } from 'core/FirebaseEvents/constants'

import { ReactComponent as DownloadSvg } from '../../icons/ico-download.svg'
import { RootState } from '../../store/reducers'

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
  const logEvent = useSelector((state: RootState) => state.app.logEvent)

  const [isDownloadModalOptionOpen, setIsDownloadModalOptionOpen] =
    useState(false)

  const containerRef = useRef<HTMLDivElement | null>(null)

  useOnClickOrFocusOutside(containerRef, () => {
    setIsDownloadModalOptionOpen(false)
  })

  return (
    <div ref={containerRef}>
      <div className={style['downloadModalButton']}>
        <button
          className="primary-button"
          disabled={isDownloading || isLocalLoading || isFiltersDisabled}
          onClick={() => {
            logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS, {
              from: location.pathname,
            })
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
              logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
                from: location.pathname,
              })
              downloadFunction(filters, 'XLS')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
            type="button"
          >
            <DownloadSvg />
            Microsoft Excel (.xls)
          </button>
          <button
            className={style['insideModalButton']}
            onClick={() => {
              logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
                from: location.pathname,
              })
              downloadFunction(filters, 'CSV')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
            type="button"
          >
            <DownloadSvg />
            Fichier CSV (.csv)
          </button>
        </div>
      )}
    </div>
  )
}

export default MultiDownloadButtonsModal
