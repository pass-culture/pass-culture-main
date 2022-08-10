import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualStepper } from 'new_components/OfferIndividualStepper'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'

interface ITemplateProps {
  children: JSX.Element
  withStepper?: boolean
}

const Template = ({ children, withStepper = true }: ITemplateProps) => {
  const { offer } = useOfferIndividualContext()
  const isCreation = useIsCreation()
  return (
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>{isCreation ? 'Créer une offre' : 'Editez votre offre'}</h1>
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
