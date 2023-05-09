import React from 'react'

import { OfferFormLayout } from 'components/OfferFormLayout'
import { OfferIndividualBreadcrumb } from 'components/OfferIndividualBreadcrumb'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { Status } from '../Status'

import OfferStatusBanner from './OfferStatusBanner'
import styles from './Template.module.scss'

export interface ITemplateProps {
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
}: ITemplateProps) => {
  const { offer, setOffer, shouldTrack } = useOfferIndividualContext()
  const mode = useOfferWizardMode()
  const notify = useNotification()

  /* istanbul ignore next: DEBT, TO FIX */
  const reloadOffer = async () => {
    const response = await getOfferIndividualAdapter(offer?.nonHumanizedId)
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
        offerId={offer.nonHumanizedId}
        status={offer.status}
        isActive={offer.isActive}
        canDeactivate={mode !== OFFER_WIZARD_MODE.DRAFT}
        reloadOffer={reloadOffer}
      />
    )

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
      {withStepper && (
        <OfferFormLayout.Stepper>
          <OfferIndividualBreadcrumb shouldTrack={shouldTrack} />
        </OfferFormLayout.Stepper>
      )}

      <OfferFormLayout.Content>{children}</OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Template
