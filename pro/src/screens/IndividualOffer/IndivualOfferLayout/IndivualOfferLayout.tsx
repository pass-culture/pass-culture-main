import React from 'react'

import { IndividualOfferBreadcrumb } from 'components/IndividualOfferBreadcrumb/IndividualOfferBreadcrumb'
import { OfferFormLayout } from 'components/OfferFormLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { Status } from '../Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'

import styles from './IndivualOfferLayout.module.scss'
import OfferStatusBanner from './OfferStatusBanner/OfferStatusBanner'

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
    <OfferFormLayout>
      {title !== null && (
        <OfferFormLayout.TitleBlock
          className={!offer?.name ? styles['title-without-name'] : undefined}
          actions={actions}
        >
          <h1>{title ? title : defaultTitle}</h1>
          {offer && <h4>{offer.name}</h4>}
        </OfferFormLayout.TitleBlock>
      )}

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}

      {withStepper && (
        <OfferFormLayout.Stepper>
          <IndividualOfferBreadcrumb />
        </OfferFormLayout.Stepper>
      )}

      <OfferFormLayout.Content>{children}</OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default IndivualOfferLayout
