import classnames from 'classnames'
import { format } from 'date-fns-tz'
import type React from 'react'
import { useRef, useState } from 'react'

import type { OfferStockResponse } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { hasErrorCode } from '@/apiClient/helpers'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { LOGS_DATA } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullStockIcon from '@/icons/full-stock.svg'
import strokeHourglass from '@/icons/stroke-hourglass.svg'

import styles from './PrebookingButton.module.scss'
import { PrebookingModal } from './PrebookingModal'

export interface PrebookingButtonProps {
  className?: string
  stock: OfferStockResponse
  canPrebookOffers: boolean
  queryId: string
  isInSuggestions?: boolean
  label?: string
  hideLimitDate?: boolean
  isPreview?: boolean
  setInstitutionOfferCount?: (value: number) => void
  institutionOfferCount?: number
  setOfferPrebooked?: (value: boolean) => void
  shouldDisablePrebookButton: boolean
  refToFocusOnOfferPrebooked?: React.RefObject<HTMLElement>
}

export const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
  queryId,
  isInSuggestions,
  label = 'Préréserver l’offre',
  hideLimitDate,
  isPreview = false,
  setInstitutionOfferCount,
  institutionOfferCount,
  setOfferPrebooked,
  shouldDisablePrebookButton,
  refToFocusOnOfferPrebooked,
}: PrebookingButtonProps): JSX.Element | null => {
  const [hasPrebookedOffer, setHasPrebookedOffer] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const snackBar = useSnackBar()

  const prebookButtonRef = useRef<HTMLButtonElement>(null)

  const handleBookingModalButtonClick = (stockId: number) => {
    if (LOGS_DATA && !isPreview) {
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

    setTimeout(() => {
      if (!prebookButtonRef.current) {
        refToFocusOnOfferPrebooked?.current?.focus()
      }
    })
  }

  const preBookCurrentStock = async () => {
    try {
      await apiAdage.bookCollectiveOffer({ stockId: stock.id })
    } catch (error) {
      if (hasErrorCode(error)) {
        if (error.body.code === 'WRONG_UAI_CODE') {
          snackBar.error(
            'Cette offre n’est pas préréservable par votre établissement'
          )
        } else if (error.body.code === 'UNKNOWN_EDUCATIONAL_INSTITUTION') {
          snackBar.error(
            'Votre établissement scolaire n’est pas recensé dans le dispositif pass Culture'
          )
        }
      } else {
        snackBar.error(
          'Impossible de préréserver cette offre.\nVeuillez contacter le support'
        )
      }

      return
    }

    setHasPrebookedOffer(true)

    if (!isPreview) {
      setInstitutionOfferCount?.(
        institutionOfferCount ? institutionOfferCount - 1 : 0
      )
    }
    setOfferPrebooked?.(true)
    closeModal()
    snackBar.success('Votre préréservation a été effectuée avec succès')
  }

  return canPrebookOffers ? (
    <>
      <div
        className={classnames(styles['prebooking-button-container'], className)}
      >
        {hasPrebookedOffer ? (
          <Tag
            label="Préréservé"
            variant={TagVariant.WARNING}
            icon={strokeHourglass}
          />
        ) : (
          <div className={styles['prebooking-button-container']}>
            <Button
              icon={fullStockIcon}
              onClick={() => handleBookingModalButtonClick(stock.id)}
              disabled={shouldDisablePrebookButton}
              ref={prebookButtonRef}
              label={label}
            />

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

      <PrebookingModal
        closeModal={closeModal}
        preBookCurrentStock={preBookCurrentStock}
        isPreview={isPreview}
        isDialogOpen={isModalOpen}
        refToFocusOnClose={prebookButtonRef}
      />
    </>
  ) : null
}
