import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { musicOptionsTree } from 'core/Offers/categoriesSubTypes'
import FormLayout from 'new_components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

const MusicTypes = (): JSX.Element => {
  const [musicTypesOptions, setMusicTypesOptions] = useState<{
    musicType: SelectOptions
    musicSubType: SelectOptions
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
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(() => {
    setFieldValue('musicSubType', FORM_DEFAULT_VALUES.musicSubType)
    let newMusicSubTypeOptions: SelectOptions = []
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
      <FormLayout.Row smSpaceAfter={true}>
        <Select
          label="Choisir un genre musical"
          name="musicType"
          options={musicTypesOptions.musicType}
          defaultOption={{
            label: 'Choisir un genre musical',
            value: FORM_DEFAULT_VALUES.musicType,
          }}
        />
      </FormLayout.Row>

      {musicTypesOptions.musicSubType.length > 0 && (
        <FormLayout.Row smSpaceAfter={true}>
          <Select
            label="Choisir un sous-genre"
            name="musicSubType"
            options={musicTypesOptions.musicSubType}
            defaultOption={{
              label: 'Choisir un sous-genre',
              value: FORM_DEFAULT_VALUES.musicSubType,
            }}
          />
        </FormLayout.Row>
      )}
    </>
  )
}

export default MusicTypes
