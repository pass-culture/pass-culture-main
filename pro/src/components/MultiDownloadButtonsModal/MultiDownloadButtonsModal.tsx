import React, { useRef, useState } from 'react'

import { TPreFilters } from 'core/Bookings'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useOnClickOrFocusOutside from 'hooks/useOnClickOrFocusOutside'
import { ReactComponent as DownloadSvg } from 'icons/full-download.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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
  const { logEvent } = useAnalytics()

  const [isDownloadModalOptionOpen, setIsDownloadModalOptionOpen] =
    useState(false)

  const containerRef = useRef<HTMLDivElement | null>(null)

  useOnClickOrFocusOutside(containerRef, () => {
    setIsDownloadModalOptionOpen(false)
  })

  return (
    <div ref={containerRef} className={style['download-button-box']}>
      <div className={style['download-modal-button']}>
        <button
          className="primary-button"
          disabled={isDownloading || isLocalLoading || isFiltersDisabled}
          onClick={() => {
            logEvent?.(Events.CLICKED_DOWNLOAD_BOOKINGS, {
              from: location.pathname,
            })
            setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
          }}
          type="button"
        >
          Télécharger
          {isDownloadModalOptionOpen ? (
            <DropUpIcon className={style['drop-icon']} />
          ) : (
            <DropDownIcon className={style['drop-icon']} />
          )}
        </button>
      </div>
      {isDownloadModalOptionOpen && (
        <div className={style['download-modal-option']}>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={DownloadSvg}
            className={style['inside-modal-button']}
            onClick={() => {
              logEvent?.(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
                from: location.pathname,
              })
              downloadFunction(filters, 'XLS')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
          >
            Microsoft Excel (.xls)
          </Button>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={DownloadSvg}
            className={style['inside-modal-button']}
            onClick={() => {
              logEvent?.(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
                from: location.pathname,
              })
              downloadFunction(filters, 'CSV')
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
          >
            Fichier CSV (.csv)
          </Button>
        </div>
      )}
    </div>
  )
}

export default MultiDownloadButtonsModal
