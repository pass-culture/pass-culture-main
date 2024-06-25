import cn from 'classnames'
import { format } from 'date-fns'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import fullWaitIcon from 'icons/full-wait.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm, isDateValid } from 'utils/date'

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
  const isFutureOfferEnabled = useActiveFeature('WIP_FUTURE_OFFER')
  const formattedDate = isDateValid(offer?.publicationDate)
    ? format(new Date(offer.publicationDate), FORMAT_DD_MM_YYYY)
    : ''
  const formattedTime = isDateValid(offer?.publicationDate)
    ? format(new Date(offer.publicationDate), FORMAT_HH_mm)
    : ''
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

        {isFutureOfferEnabled &&
          mode !== OFFER_WIZARD_MODE.CREATION &&
          isDateValid(offer?.publicationDate) &&
          new Date(offer.publicationDate) > new Date() && (
            <div className={styles['publication-date']}>
              <SvgIcon
                src={fullWaitIcon}
                alt=""
                className={styles['publication-icon']}
                width="24"
              />
              Publication prévue le {formattedDate} à {formattedTime}
            </div>
          )}
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
