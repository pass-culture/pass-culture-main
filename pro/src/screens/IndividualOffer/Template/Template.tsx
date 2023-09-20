import React from 'react'

import { IndividualOfferBreadcrumb } from 'components/IndividualOfferBreadcrumb'
import { OfferFormLayout } from 'components/OfferFormLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { Status } from '../Status'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'

import OfferStatusBanner from './OfferStatusBanner'
import styles from './Template.module.scss'

export interface TemplateProps {
  title?: string
  withStepper?: boolean
  withStatus?: boolean
  withBanner?: boolean
  children: JSX.Element | JSX.Element[]
}

const Template = ({
  title,
  children,
  withStepper = true,
  withStatus = true,
  withBanner = true,
}: TemplateProps) => {
  const { offer, setOffer, shouldTrack } = useIndividualOfferContext()
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
    [OFFER_WIZARD_MODE.EDITION]: 'Modifier l’offre',
  }[mode]

  const actions = mode !== OFFER_WIZARD_MODE.CREATION &&
    offer &&
    withStatus && (
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
      {offer && withBanner && <OfferStatusBanner status={offer.status} />}
      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}

      {withStepper && (
        <OfferFormLayout.Stepper>
          <IndividualOfferBreadcrumb shouldTrack={shouldTrack} />
        </OfferFormLayout.Stepper>
      )}

      <OfferFormLayout.Content>{children}</OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Template
