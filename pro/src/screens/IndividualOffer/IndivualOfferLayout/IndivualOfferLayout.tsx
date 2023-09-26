import cn from 'classnames'
import React from 'react'

import { IndividualOfferBreadcrumb } from 'components/IndividualOfferBreadcrumb/IndividualOfferBreadcrumb'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import Status from '../Status/Status'
import SynchronizedProviderInformation from '../SynchronisedProviderInfos/SynchronizedProviderInformation'

import OfferStatusBanner from './OfferStatusBanner/OfferStatusBanner'
import styles from './Template.module.scss'

export interface IndivualOfferLayoutProps {
  title?: string
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
}

const IndivualOfferLayout = ({
  title,
  children,
  withStepper = true,
}: IndivualOfferLayoutProps) => {
  const { offer, setOffer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const notify = useNotification()

  /* istanbul ignore next: DEBT, TO FIX */
  const reloadOffer = async () => {
    const response = await getIndividualOfferAdapter(offer?.id)
    if (response.isOk) {
      setOffer && setOffer(response.payload)
    } else {
      notify.error(response.message)
    }
  }

  const defaultTitle = {
    [OFFER_WIZARD_MODE.CREATION]: 'Créer une offre',
    [OFFER_WIZARD_MODE.DRAFT]: 'Compléter l’offre',
    [OFFER_WIZARD_MODE.READ_ONLY]: 'Consulter l’offre',
    [OFFER_WIZARD_MODE.EDITION]: 'Modifier l’offre',
  }[mode]

  const actions = mode !== OFFER_WIZARD_MODE.CREATION &&
    offer &&
    withStepper && (
      <Status
        offerId={offer.id}
        status={offer.status}
        isActive={offer.isActive}
        canDeactivate={mode !== OFFER_WIZARD_MODE.DRAFT}
        reloadOffer={reloadOffer}
      />
    )
  const providerName = offer?.lastProviderName

  return (
    <div>
      {title !== null && (
        <div
          className={cn(styles['title'], {
            [styles['title-without-name']]: !offer?.name,
          })}
        >
          <div>
            <h1>{title ? title : defaultTitle}</h1>
            {offer && <h4 className={styles['offer-title']}>{offer.name}</h4>}
          </div>
          {actions && <div className={styles['right']}>{actions}</div>}
        </div>
      )}

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}

      {withStepper && <IndividualOfferBreadcrumb />}

      <div className={styles['content']}>{children}</div>
    </div>
  )
}

export default IndivualOfferLayout
