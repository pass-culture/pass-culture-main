import cn from 'classnames'
import { Navigate, useLocation, useNavigate } from 'react-router'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { useNotification } from 'commons/hooks/useNotification'
import { formatDateTimeParts, isDateValid } from 'commons/utils/date'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { BackToNavLink } from 'components/BackToNavLink/BackToNavLink'
import { IndividualOfferNavigation } from 'components/IndividualOfferNavigation/IndividualOfferNavigation'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullTrashIcon from 'icons/full-trash.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED } from 'pages/IndividualOffer/IndividualOfferInformations/components/IndividualOfferInformationsScreen'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Status } from '../Status/Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos/SynchronizedProviderInformation'

import styles from './IndividualOfferLayout.module.scss'
import { OfferStatusBanner } from './OfferStatusBanner/OfferStatusBanner'

export interface IndividualOfferLayoutProps {
  title: string
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
  offer: GetIndividualOfferWithAddressResponseModel | null
  mode: OFFER_WIZARD_MODE
  venueHasPublishedOfferWithSameEan?: boolean
}

export const IndividualOfferLayout = ({
  title,
  children,
  withStepper = true,
  offer,
  mode,
  venueHasPublishedOfferWithSameEan,
}: IndividualOfferLayoutProps) => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  const { date: publicationDate, time: publicationTime } = formatDateTimeParts(
    offer?.publicationDate
  )
  const notify = useNotification()
  const navigate = useNavigate()

  const shouldDisplayActionOnStatus =
    mode !== OFFER_WIZARD_MODE.CREATION && offer && withStepper

  // This is used to not be able to go to next step in creation mode
  const isUsefulInformationSubmitted =
    (storageAvailable('localStorage') &&
      !!localStorage.getItem(
        `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer?.id}`
      )) ||
    mode !== OFFER_WIZARD_MODE.CREATION

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  const onDeleteOfferWithAlreadyExistingEan = async () => {
    if (!offer) {
      return
    }
    try {
      await api.deleteDraftOffers({ ids: [offer.id] })
    } catch {
      notify.error(
        'Une erreur s’est produite lors de la suppression de l’offre'
      )
      return
    }
    notify.success('Votre brouillon a bien été supprimé')
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/offres')
  }

  return (
    <>
      <div
        className={cn({
          [styles['title-without-name']]: !offer?.name,
        })}
      >
        <div className={styles['title-container']}>
          <div className={styles['title-and-back-to-nav-link']}>
            <h1 className={styles['title']}>{title}</h1>
            <BackToNavLink className={styles['back-to-nav-link']} />
          </div>
          {shouldDisplayActionOnStatus && (
            <span className={styles['status']}>{<Status offer={offer} />}</span>
          )}
        </div>

        {offer && (
          <p className={styles['offer-title']}>
            {offer.name}
            {offer.isHeadlineOffer && (
              <Tag label="Offre à la une" variant={TagVariant.HEADLINE} />
            )}
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

      {venueHasPublishedOfferWithSameEan && (
        <Callout
          variant={CalloutVariant.ERROR}
          title="Votre brouillon d’offre est obsolète car vous avez déjà publié une offre avec cet EAN"
          className={styles['ean-already-exists-callout']}
        >
          <p className={styles['ean-already-exists-callout-description']}>
            Vous ne pouvez pas publier 2 offres avec un EAN similaire.
          </p>
          <Button
            onClick={onDeleteOfferWithAlreadyExistingEan}
            variant={ButtonVariant.TERNARY}
            icon={fullTrashIcon}
            className={styles['ean-already-exists-callout-button']}
          >
            Supprimer ce brouillon
          </Button>
        </Callout>
      )}

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
