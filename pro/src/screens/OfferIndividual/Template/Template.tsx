import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualStepper } from 'new_components/OfferIndividualStepper'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'

export interface ITemplateProps {
  title?: string
  withStepper?: boolean
  children: JSX.Element
}

const Template = ({ title, children, withStepper = true }: ITemplateProps) => {
  const { offer } = useOfferIndividualContext()
  const isCreation = useIsCreation()

  const defaultTitle = isCreation ? 'Créer une offre' : "Modifier l'offre"

  return (
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>{title ? title : defaultTitle}</h1>
      </OfferFormLayout.TitleBlock>

      <OfferFormLayout.TitleBlock>
        {offer && <h4>{offer.name}</h4>}
      </OfferFormLayout.TitleBlock>

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
