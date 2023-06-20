import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { musicOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { Select } from 'ui-kit'

interface IMusicTypesProps {
  readOnly?: boolean
}

const MusicTypes = ({ readOnly = false }: IMusicTypesProps): JSX.Element => {
  const [musicTypesOptions, setMusicTypesOptions] = useState<{
    musicType: SelectOption[]
    musicSubType: SelectOption[]
  }>({
    musicType: musicOptionsTree
      .map(data => ({
        value: data.code.toString(),
        label: data.label,
      }))
      .sort((a, b) => a.label.localeCompare(b.label, 'fr')),
    musicSubType: [],
  })

  const {
    values: { musicType },
    initialValues,
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(() => {
    setFieldValue('musicSubType', initialValues.musicSubType)
    let newMusicSubTypeOptions: SelectOption[] = []
    if (musicType !== FORM_DEFAULT_VALUES.musicType) {
      const selectedMusicTypeChildren = musicOptionsTree.find(
        musicTypeOption => musicTypeOption.code === parseInt(musicType)
      )?.children

      if (selectedMusicTypeChildren) {
        newMusicSubTypeOptions = selectedMusicTypeChildren
          .map(data => ({
            value: data.code.toString(),
            label: data.label,
          }))
          .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
      }
    }

    setMusicTypesOptions(prevOptions => {
      return {
        ...prevOptions,
        musicSubType: newMusicSubTypeOptions,
      }
    })
  }, [musicType])

  return (
    <>
      <FormLayout.Row>
        <Select
          label="Genre musical"
          name="musicType"
          options={musicTypesOptions.musicType}
          defaultOption={{
            label: 'Choisir un genre musical',
            value: FORM_DEFAULT_VALUES.musicType,
          }}
          disabled={readOnly}
        />
      </FormLayout.Row>

      {musicTypesOptions.musicSubType.length > 0 && (
        <FormLayout.Row>
          <Select
            label="Sous-genre"
            name="musicSubType"
            options={musicTypesOptions.musicSubType}
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

export default MusicTypes
