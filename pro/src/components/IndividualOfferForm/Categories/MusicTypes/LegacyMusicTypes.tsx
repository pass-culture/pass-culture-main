import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { musicOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { Select } from 'ui-kit'

interface MusicTypesProps {
  readOnly?: boolean
}

const getMusicSubTypeOptions = (
  musicType: string = FORM_DEFAULT_VALUES.musicType
): SelectOption[] => {
  if (musicType === FORM_DEFAULT_VALUES.musicType) {
    return []
  }

  const selectedMusicTypeChildren =
    musicOptionsTree.find(
      (musicTypeOption) => musicTypeOption.code === parseInt(musicType)
    )?.children ?? []

  return selectedMusicTypeChildren
    .map((data) => ({
      value: data.code.toString(),
      label: data.label,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

const LegacyMusicTypes = ({
  readOnly = false,
}: MusicTypesProps): JSX.Element => {
  const {
    values: { musicType },
  } = useFormikContext<IndividualOfferFormValues>()

  const musicTypeOptions = musicOptionsTree
    .map((data) => ({
      value: data.code.toString(),
      label: data.label,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  const musicSubTypeOptions = getMusicSubTypeOptions(musicType)

  return (
    <>
      <FormLayout.Row>
        <Select
          label="Genre musical"
          name="musicType"
          options={musicTypeOptions}
          defaultOption={{
            label: 'Choisir un genre musical',
            value: FORM_DEFAULT_VALUES.musicType,
          }}
          disabled={readOnly}
        />
      </FormLayout.Row>

      {musicSubTypeOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            label="Sous-genre"
            name="musicSubType"
            options={musicSubTypeOptions}
            defaultOption={{
              label: 'Choisir un sous-genre',
              value: FORM_DEFAULT_VALUES.musicSubType,
            }}
            disabled={readOnly}
          />
        </FormLayout.Row>
      )}
    </>
  )
}

export default LegacyMusicTypes
