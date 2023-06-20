import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { TextArea, TextInput } from 'ui-kit'
import DurationInput from 'ui-kit/form/DurationInput'

import styles from '../OfferIndividualForm.module.scss'
import { IOfferIndividualFormValues } from '../types'

export interface IInformationsProps {
  readOnlyFields?: string[]
}

const Informations = ({
  readOnlyFields = [],
}: IInformationsProps): JSX.Element => {
  const {
    values: { subCategoryFields },
  } = useFormikContext<IOfferIndividualFormValues>()

  const hasAuthor = subCategoryFields.includes('author')
  const hasPerformer = subCategoryFields.includes('performer')
  const hasEan = subCategoryFields.includes('ean')
  const hasSpeaker = subCategoryFields.includes('speaker')
  const hasStageDirector = subCategoryFields.includes('stageDirector')
  const hasVisa = subCategoryFields.includes('visa')
  const hasDurationMinutes = subCategoryFields.includes('durationMinutes')

  return (
    <FormLayout.Section title="Informations artistiques">
      <FormLayout.Row>
        <TextInput
          countCharacters
          label="Titre de l’offre"
          maxLength={90}
          name="name"
          disabled={readOnlyFields.includes('name')}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea
          countCharacters
          isOptional
          label="Description"
          maxLength={1000}
          name="description"
          disabled={readOnlyFields.includes('description')}
        />
      </FormLayout.Row>
      {hasSpeaker && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="Intervenant"
            maxLength={1000}
            name="speaker"
            disabled={readOnlyFields.includes('speaker')}
          />
        </FormLayout.Row>
      )}
      {hasAuthor && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="Auteur"
            maxLength={1000}
            name="author"
            disabled={readOnlyFields.includes('author')}
          />
        </FormLayout.Row>
      )}
      {hasVisa && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="Visa d’exploitation"
            maxLength={1000}
            name="visa"
            disabled={readOnlyFields.includes('visa')}
          />
        </FormLayout.Row>
      )}
      {hasStageDirector && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="Metteur en scène"
            maxLength={1000}
            name="stageDirector"
            disabled={readOnlyFields.includes('stageDirector')}
          />
        </FormLayout.Row>
      )}
      {hasPerformer && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="Interprète"
            maxLength={1000}
            name="performer"
            disabled={readOnlyFields.includes('performer')}
          />
        </FormLayout.Row>
      )}
      {hasEan && (
        <FormLayout.Row>
          <TextInput
            isOptional
            label="EAN"
            name="ean"
            maxLength={13}
            disabled={readOnlyFields.includes('ean')}
          />
        </FormLayout.Row>
      )}

      {hasDurationMinutes && (
        <FormLayout.Row>
          <DurationInput
            isOptional
            label={'Durée'}
            name="durationMinutes"
            className={styles['input-duration-minutes']}
            disabled={readOnlyFields.includes('durationMinutes')}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Informations
