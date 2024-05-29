import cn from 'classnames'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

import { Status } from '../Status/Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos/SynchronizedProviderInformation'

import styles from './IndivualOfferLayout.module.scss'
import { OfferStatusBanner } from './OfferStatusBanner/OfferStatusBanner'

export interface IndivualOfferLayoutProps {
  title: string
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
  offer: GetIndividualOfferResponseModel | null
  mode: OFFER_WIZARD_MODE
}

export const IndivualOfferLayout = ({
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
        className={cn({
          [styles['title-without-name']]: !offer?.name,
        })}
      >
        <div className={styles['title-container']}>
          <h1 className={styles['title']}>{title}</h1>
          {shouldDisplayActionOnStatus && (
            <span className={styles['status']}>
              {
                <Status
                  offerId={offer.id}
                  status={offer.status}
                  isActive={offer.isActive}
                  canDeactivate={offer.isActivable}
                />
              }
            </span>
          )}
        </div>
        {offer && <p className={styles['offer-title']}>{offer.name}</p>}
      </div>
      {offer && withStepper && <OfferStatusBanner status={offer.status} />}
      {offer?.lastProvider?.name && (
        <SynchronizedProviderInformation
          providerName={offer.lastProvider.name}
        />
      )}
      {withStepper && <IndividualOfferNavigation />}
      <div className={styles['content']}>{children}</div>
    </>
  )
}
