import cn from 'classnames'
import React from 'react'

import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'

import Status from '../Status/Status'
import SynchronizedProviderInformation from '../SynchronisedProviderInfos/SynchronizedProviderInformation'

import styles from './IndivualOfferLayout.module.scss'
import OfferStatusBanner from './OfferStatusBanner/OfferStatusBanner'

export interface IndivualOfferLayoutProps {
  title: string
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
  offer: IndividualOffer | null
  mode: OFFER_WIZARD_MODE
}

const IndivualOfferLayout = ({
  title,
  children,
  withStepper = true,
  offer,
  mode,
}: IndivualOfferLayoutProps) => {
  const shouldDisplayActionOnStatus =
    mode !== OFFER_WIZARD_MODE.CREATION && offer && withStepper

  return (
    <>
      <div
        className={cn(styles['title'], {
          [styles['title-without-name']]: !offer?.name,
        })}
      >
        <div>
          <h1>
            {title}{' '}
            {offer && (
              <span className={styles['offer-title']}>{offer.name}</span>
            )}
          </h1>
        </div>
        {shouldDisplayActionOnStatus && (
          <div className={styles['right']}>
            {
              <Status
                offerId={offer.id}
                status={offer.status}
                isActive={offer.isActive}
                canDeactivate={offer.isActivable}
              />
            }
          </div>
        )}
      </div>

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {offer?.lastProvider?.name && (
        <SynchronizedProviderInformation
          providerName={offer?.lastProvider?.name}
        />
      )}

      {withStepper && <IndividualOfferNavigation />}

      <div className={styles['content']}>{children}</div>
    </>
  )
}

export default IndivualOfferLayout
