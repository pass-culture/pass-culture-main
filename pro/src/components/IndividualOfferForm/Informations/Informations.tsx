import { useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

import styles from '../IndividualOfferForm.module.scss'
import { IndividualOfferFormValues } from '../types'

export interface InformationsProps {
  readOnlyFields?: string[]
}

export const Informations = ({
  readOnlyFields = [],
}: InformationsProps): JSX.Element => {
  const {
    values: { subCategoryFields },
  } = useFormikContext<IndividualOfferFormValues>()

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
            label="EAN-13 (European Article Numbering)"
            countCharacters
            name="ean"
            maxLength={13}
            disabled={readOnlyFields.includes('ean')}
          />
        </FormLayout.Row>
      )}
      {hasDurationMinutes && (
        <FormLayout.Row>
          <TimePicker
            isOptional
            label={'Durée'}
            name="durationMinutes"
            className={styles['input-duration-minutes']}
            disabled={readOnlyFields.includes('durationMinutes')}
            showIntervalList={false}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}
