import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualStepper } from 'new_components/OfferIndividualStepper'

import styles from './Template.module.scss'

export interface ITemplateProps {
  // TODO: remove this '| null' on OFFER_FORM_V3 FF cleaning
  title?: string | null
  withStepper?: boolean
  children: JSX.Element | JSX.Element[]
}

const Template = ({ title, children, withStepper = true }: ITemplateProps) => {
  const { offer } = useOfferIndividualContext()
  const mode = useOfferWizardMode()

  const defaultTitle = {
    [OFFER_WIZARD_MODE.CREATION]: 'Créer une offre',
    [OFFER_WIZARD_MODE.DRAFT]: "Compléter l'offre",
    [OFFER_WIZARD_MODE.EDITION]: "Modifier l'offre",
  }[mode]
  return (
    <OfferFormLayout>
      {title !== null && (
        <>
          <OfferFormLayout.TitleBlock
            className={!offer?.name ? styles['title-without-name'] : undefined}
          >
            <h1>{title ? title : defaultTitle}</h1>
          </OfferFormLayout.TitleBlock>

          <OfferFormLayout.TitleBlock>
            {offer && <h4>{offer.name}</h4>}
          </OfferFormLayout.TitleBlock>
        </>
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
