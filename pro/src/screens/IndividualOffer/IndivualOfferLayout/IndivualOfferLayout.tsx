import cn from 'classnames'
import React from 'react'

import { IndividualOfferBreadcrumb } from 'components/IndividualOfferBreadcrumb/IndividualOfferBreadcrumb'
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
  setOffer: ((offer: IndividualOffer | null) => void) | null
  mode: OFFER_WIZARD_MODE
}

const IndivualOfferLayout = ({
  title,
  children,
  withStepper = true,
  offer,
  setOffer,
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
          <h1>{title}</h1>
          {offer && <h4 className={styles['offer-title']}>{offer.name}</h4>}
        </div>
        {shouldDisplayActionOnStatus && (
          <div className={styles['right']}>
            {
              <Status
                offerId={offer.id}
                status={offer.status}
                isActive={offer.isActive}
                canDeactivate={mode !== OFFER_WIZARD_MODE.DRAFT}
                setOffer={setOffer}
              />
            }
          </div>
        )}
      </div>

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {offer?.lastProviderName && (
        <SynchronizedProviderInformation
          providerName={offer?.lastProviderName}
        />
      )}

      {withStepper && <IndividualOfferBreadcrumb />}

      <div className={styles['content']}>{children}</div>
    </>
  )
}

export default IndivualOfferLayout
