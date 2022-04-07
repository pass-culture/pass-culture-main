import React from 'react'
import { useFormikContext } from 'formik'

// import { DEFAULT_INDIVIDUAL_FORM_VALUES } from 'core/Offers'
import { IOfferIndividualFormValues } from 'core/Offers/types'
import FormLayout from 'new_components/FormLayout'
import { TextArea, TextInput } from 'ui-kit'

import { LABELS } from '../constants'

interface IInformationsProps {}

const Informations = ({}: IInformationsProps): JSX.Element => {
  // GOAL: handle section valiation and interact with global form
  const { values, setFieldValue } =
    useFormikContext<IOfferIndividualFormValues>()
  return (
    <div>
      <h2 style={{ color: 'blue' }}>screen: Informations</h2>
      <FormLayout.Section
        description="Le type de l’offre permet de la caractériser et de la valoriser au mieux pour les enseignants et chefs d’établissement."
        title="Type d’offre"
      >
        <FormLayout.Row>
          <TextInput
            countCharacters
            label={LABELS['title']}
            maxLength={90}
            name="title"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextArea
            countCharacters
            isOptional
            label={LABELS['description']}
            maxLength={1000}
            name="description"
            placeholder="Détaillez ici votre projet et son interêt pédagogique"
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </div>
  )
}

export default Informations
