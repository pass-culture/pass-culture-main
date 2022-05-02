import React, { useEffect, useState } from 'react'
import { useFormikContext } from 'formik'

import {
  musicOptionsTree,
} from 'components/pages/Offers/Offer/OfferDetails/OfferForm/OfferCategories/subTypes'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

import { buildSelectOptions } from '../utils'

interface IType {
  code: number
  label: string
}

interface IOption {
  value: string
  label: string
}

interface IMusicTypesOptions {
  musicType: IOption[]
  musicSubType: IOption[]
}

const initialMusicTypesOptions = {
  musicType: buildSelectOptions<IType>(c => c.code, c =>c.label, musicOptionsTree),
  musicSubType: [],
}

const MusicTypes = (): JSX.Element => {
  const [musicTypesOptions, setMusicTypesOptions] = useState<IMusicTypesOptions>(initialMusicTypesOptions)
  const { values: { musicType } } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(() => {
    if (musicType !== FORM_DEFAULT_VALUES.musicType) {
      const selectedMusicTypeChildren = musicOptionsTree.find(
        musicTypeOption => musicTypeOption.code === parseInt(musicType)
      )?.children

      if (selectedMusicTypeChildren) {
        setMusicTypesOptions(prevOptions => ({
          ...prevOptions,
          musicSubType: buildSelectOptions<IType>(
            c => c.code,
            c => c.label,
            selectedMusicTypeChildren
            )
          })
  )}
    } else {
      setMusicTypesOptions(prevOptions => ({
        ...prevOptions,
        musicSubType: initialMusicTypesOptions.musicSubType,
      }))
    }
  }, [musicType])

  return (
    <>
      <Select
        label='Choisir un genre musical'
        name='musicType'
        options={musicTypesOptions.musicType}
        defaultOption={{
          label: 'Choisir un genre musical',
          value: FORM_DEFAULT_VALUES.musicType,
        }}
      />
      {musicType && (
        <Select
          label='Choisir un sous-genre'
          name='musicSubType'
          options={musicTypesOptions.musicSubType}
          defaultOption={{
            label: 'Choisir un sous-genre',
            value: FORM_DEFAULT_VALUES.musicSubType,
          }}
        />
      )}
    </>
  )
}

export default MusicTypes
