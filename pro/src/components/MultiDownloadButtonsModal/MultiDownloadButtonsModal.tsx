import { useAnalytics } from 'app/App/analytics/firebase'
import cn from 'classnames'
import {
  CollectivePreFiltersParams,
  PreFiltersParams,
} from 'commons/core/Bookings/types'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'
import fullDownIcon from 'icons/full-down.svg'
import fullDownloadIcon from 'icons/full-download.svg'
import fullUpIcon from 'icons/full-up.svg'
import { useRef, useState } from 'react'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import style from './MultiDownloadButtonsModal.module.scss'

type MultiDownloadButtonsModalType = {
  isDownloading: boolean
  isLocalLoading: boolean
  isFiltersDisabled: boolean
  downloadFunction: (
    filters: PreFiltersParams | CollectivePreFiltersParams,
    type: 'CSV' | 'XLS'
  ) => Promise<void>
  filters: PreFiltersParams | CollectivePreFiltersParams
  className?: string
}

export const MultiDownloadButtonsModal = ({
  isDownloading,
  isLocalLoading,
  isFiltersDisabled,
  downloadFunction,
  filters,
  className,
}: MultiDownloadButtonsModalType): JSX.Element => {
  const { logEvent } = useAnalytics()

  const [isDownloadModalOptionOpen, setIsDownloadModalOptionOpen] =
    useState(false)

  const containerRef = useRef<HTMLDivElement | null>(null)

  useOnClickOrFocusOutside(containerRef, () => {
    setIsDownloadModalOptionOpen(false)
  })

  return (
    <div
      ref={containerRef}
      className={cn(style['download-button-box'], className)}
    >
      <div className={style['download-modal-button']}>
        <Button
          variant={ButtonVariant.PRIMARY}
          disabled={isDownloading || isLocalLoading || isFiltersDisabled}
          onClick={() => {
            logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS, {
              from: location.pathname,
            })
            setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
          }}
          aria-expanded={isDownloadModalOptionOpen}
          aria-controls="download-panel"
        >
          Télécharger
          {isDownloadModalOptionOpen ? (
            <SvgIcon src={fullUpIcon} alt="" className={style['drop-icon']} />
          ) : (
            <SvgIcon src={fullDownIcon} alt="" className={style['drop-icon']} />
          )}
        </Button>
      </div>

      {isDownloadModalOptionOpen && (
        <div className={style['download-modal-option']} id="download-panel">
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullDownloadIcon}
            className={style['inside-modal-button']}
            onClick={async () => {
              await downloadFunction(filters, 'XLS')
              logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
                from: location.pathname,
              })
              setIsDownloadModalOptionOpen(!isDownloadModalOptionOpen)
            }}
          >
            Microsoft Excel (.xls)
          </Button>

          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullDownloadIcon}
            className={style['inside-modal-button']}
            onClick={async () => {
              await downloadFunction(filters, 'CSV')
              logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
                from: location.pathname,
              })
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
