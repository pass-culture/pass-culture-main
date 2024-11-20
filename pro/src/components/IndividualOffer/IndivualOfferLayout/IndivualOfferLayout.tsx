import cn from 'classnames'

import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { formatDateTimeParts, isDateValid } from 'commons/utils/date'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import fullWaitIcon from 'icons/full-wait.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Status } from '../Status/Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos/SynchronizedProviderInformation'
import { LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED } from '../UsefulInformationScreen/UsefulInformationScreen'

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
  const { date: publicationDate, time: publicationTime } = formatDateTimeParts(
    offer?.publicationDate
  )
  const shouldDisplayActionOnStatus =
    mode !== OFFER_WIZARD_MODE.CREATION && offer && withStepper

  // This is used to not be able to go to next step in creation mode
  const isUsefulInformationSubmitted =
    (localStorageAvailable() &&
      !!localStorage.getItem(
        `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer?.id}`
      )) ||
    mode !== OFFER_WIZARD_MODE.CREATION

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
            <span className={styles['status']}>{<Status offer={offer} />}</span>
          )}
        </div>

        {offer && <p className={styles['offer-title']}>{offer.name}</p>}

        {mode !== OFFER_WIZARD_MODE.CREATION &&
          offer?.status !== OfferStatus.ACTIVE &&
          isDateValid(offer?.publicationDate) &&
          new Date(offer.publicationDate) > new Date() && (
            <div className={styles['publication-date']}>
              <SvgIcon
                src={fullWaitIcon}
                alt=""
                className={styles['publication-icon']}
                width="24"
              />
              Publication prévue le {publicationDate} à {publicationTime}
            </div>
          )}
      </div>

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {offer?.lastProvider?.name && (
        <div className={styles['banner-container']}>
          <SynchronizedProviderInformation
            providerName={offer.lastProvider.name}
          />
        </div>
      )}

      {withStepper && (
        <IndividualOfferNavigation
          isUsefulInformationSubmitted={isUsefulInformationSubmitted}
        />
      )}

      <div className={styles['content']}>{children}</div>
    </>
  )
}
