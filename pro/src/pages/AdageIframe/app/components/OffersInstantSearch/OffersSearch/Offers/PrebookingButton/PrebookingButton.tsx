import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import { OfferStockResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useNotification } from 'hooks/useNotification'
import fullStockIcon from 'icons/full-stock.svg'
import strokeHourglass from 'icons/stroke-hourglass.svg'
import { Button } from 'ui-kit/Button/Button'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'
import { hasErrorCode } from 'utils/error'

import styles from './PrebookingButton.module.scss'
import { PrebookingModal } from './PrebookingModal'

export interface PrebookingButtonProps {
  className?: string
  stock: OfferStockResponse
  canPrebookOffers: boolean
  offerId: number
  queryId: string
  isInSuggestions?: boolean
  children?: React.ReactNode
  hideLimitDate?: boolean
  isPreview?: boolean
  setInstitutionOfferCount?: (value: number) => void
  institutionOfferCount?: number
  setOfferPrebooked?: (value: boolean) => void
}

export const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
  offerId,
  queryId,
  isInSuggestions,
  children,
  hideLimitDate,
  isPreview = false,
  setInstitutionOfferCount,
  institutionOfferCount,
  setOfferPrebooked,
}: PrebookingButtonProps): JSX.Element | null => {
  const [hasPrebookedOffer, setHasPrebookedOffer] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const notification = useNotification()

  const handleBookingModalButtonClick = (stockId: number) => {
    if (LOGS_DATA && !isPreview) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logBookingModalButtonClick({
        iframeFrom: location.pathname,
        stockId,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    }
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  const preBookCurrentStock = useCallback(async () => {
    try {
      await apiAdage.bookCollectiveOffer({ stockId: stock.id })
    } catch (error) {
      if (hasErrorCode(error)) {
        if (error.body.code === 'WRONG_UAI_CODE') {
          notification.error(
            'Cette offre n’est pas préréservable par votre établissement'
          )
        } else if (error.body.code === 'UNKNOWN_EDUCATIONAL_INSTITUTION') {
          notification.error(
            'Votre établissement scolaire n’est pas recensé dans le dispositif pass Culture'
          )
        }
      } else {
        notification.error(
          'Impossible de préréserver cette offre.\nVeuillez contacter le support'
        )
      }

      return
    }

    setHasPrebookedOffer(true)

    !isPreview &&
      setInstitutionOfferCount?.(
        institutionOfferCount ? institutionOfferCount - 1 : 0
      )
    setOfferPrebooked && setOfferPrebooked(true)
    closeModal()
    notification.success('Votre préréservation a été effectuée avec succès')
  }, [stock.id, offerId, queryId])

  return canPrebookOffers ? (
    <>
      <div className={(styles['prebooking-button-container'], className)}>
        {hasPrebookedOffer ? (
          <div className={styles['prebooking-tag']}>
            <SvgIcon
              className="prebooking-tag-icon"
              src={strokeHourglass}
              alt=""
              width="16"
            />
            Préréservé
          </div>
        ) : (
          <div className={styles['prebooking-button-container']}>
            <Button
              icon={fullStockIcon}
              className={styles['prebooking-button']}
              onClick={() => handleBookingModalButtonClick(stock.id)}
            >
              {children ?? 'Préréserver l’offre'}
            </Button>

            {!hideLimitDate && stock.bookingLimitDatetime && (
              <span className={styles['prebooking-button-booking-limit']}>
                avant le :{' '}
                <span className={styles['prebooking-button-limit-date']}>
                  {format(new Date(stock.bookingLimitDatetime), 'dd/MM/yyyy')}
                </span>
              </span>
            )}
          </div>
        )}
      </div>

      {isModalOpen && (
        <PrebookingModal
          closeModal={closeModal}
          preBookCurrentStock={preBookCurrentStock}
          isPreview={isPreview}
        />
      )}
    </>
  ) : null
}
