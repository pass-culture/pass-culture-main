import React from 'react'

import { OfferFormLayout } from 'components/OfferFormLayout'
import { OfferIndividualStepper } from 'components/OfferIndividualStepper'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { Status } from '../Status'

import styles from './Template.module.scss'

export interface ITemplateProps {
  // TODO: remove this '| null' on OFFER_FORM_V3 FF cleaning
  title?: string | null
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
}

const Template = ({ title, children, withStepper = true }: ITemplateProps) => {
  const { offer, setOffer } = useOfferIndividualContext()
  const mode = useOfferWizardMode()
  const notify = useNotification()

  /* istanbul ignore next: DEBT, TO FIX */
  const reloadOffer = async () => {
    const response = await getOfferIndividualAdapter(offer?.id)
    if (response.isOk) {
      setOffer && setOffer(response.payload)
    } else {
      notify.error(response.message, {
        withStickyActionBar: true,
      })
    }
  }

  const defaultTitle = {
    [OFFER_WIZARD_MODE.CREATION]: 'Créer une offre',
    [OFFER_WIZARD_MODE.DRAFT]: "Compléter l'offre",
    [OFFER_WIZARD_MODE.EDITION]: "Modifier l'offre",
  }[mode]

  const actions = mode !== OFFER_WIZARD_MODE.CREATION && offer && (
    <Status
      offerId={offer.id}
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

      {withStepper && (
        <OfferFormLayout.Stepper>
          <OfferIndividualStepper />
        </OfferFormLayout.Stepper>
      )}

      <OfferFormLayout.Content>{children}</OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Template
