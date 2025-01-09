import cn from 'classnames'

import { GetIndividualOfferWithAddressResponseModel, OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { formatDateTimeParts, isDateValid } from 'commons/utils/date'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { HeadlineOfferTag } from 'components/HeadlineOfferTag/HeadlineOfferTag'
import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import fullWaitIcon from 'icons/full-wait.svg'
import { LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED } from 'pages/IndividualOffer/IndividualOfferInformations/components/IndividualOfferInformationsScreen'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Status } from '../Status/Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos/SynchronizedProviderInformation'

import styles from './IndivualOfferLayout.module.scss'
import { OfferStatusBanner } from './OfferStatusBanner/OfferStatusBanner'

export interface IndivualOfferLayoutProps {
  title: string
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
  offer: GetIndividualOfferWithAddressResponseModel | null
  mode: OFFER_WIZARD_MODE
}

export const IndivualOfferLayout = ({
  title,
  children,
  withStepper = true,
  offer,
  mode,
}: IndivualOfferLayoutProps) => {
  const offerHeadlineEnabled = useActiveFeature('WIP_HEADLINE_OFFER')
  const { date: publicationDate, time: publicationTime } = formatDateTimeParts(
    offer?.publicationDate
  )
  const shouldDisplayActionOnStatus =
    mode !== OFFER_WIZARD_MODE.CREATION && offer && withStepper

  // This is used to not be able to go to next step in creation mode
  const isUsefulInformationSubmitted =
    (storageAvailable('localStorage') &&
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

        {offer && (
          <p className={styles['offer-title']}>
            {offer.name}
            {offerHeadlineEnabled && offer.isHeadlineOffer && <HeadlineOfferTag className={styles['offer-title-headline-tag']} />}
          </p>
        )}

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
