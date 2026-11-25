import { useEffect } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import { ArtistType, FieldEnum } from '@/apiClient/v1'
import {
  HasCapability,
  OfferCapabilityProvider,
} from '@/commons/core/Offers/utils/offerCapabilityContext/offerCapabilityContext'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { ArtistField } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/DetailsSubForm/components/ArtistField/ArtistField'
import type { DescriptionFormValues } from '@/pages/IndividualOfferV2/IndividualOfferV2Description/validationSchemaV2'
import { Select } from '@/ui-kit/form/Select/Select'

import { DEFAULT_DESCRIPTION_FORM_VALUES } from '../constants'
import styles from '../IndividualOfferV2Description.module.scss'

interface IndividualOfferV2DescriptionExtraData {
  readOnlyFields: string[]
  capabilities: FieldEnum[]
  mandatoryFields: string[]
}

export const IndividualOfferV2DescriptionExtraData = ({
  readOnlyFields,
  capabilities,
  mandatoryFields,
}: IndividualOfferV2DescriptionExtraData): JSX.Element => {
  const {
    control,
    register,
    getValues,
    setValue,
    formState: { errors },
  } = useFormContext<DescriptionFormValues>()

  const artistFieldArray = useFieldArray({
    control,
    name: 'artistOfferLinks',
  })

  const { musicTypes } = useMusicTypes()

  const musicTypesOptions = musicTypes.map((data) => ({
    value: data.gtl_id,
    label: data.label,
  }))

  // Music types are fetched asynchronously: the saved genre can only be selected once its option exists.
  useEffect(() => {
    if (musicTypes.length > 0) {
      setValue('extraData.gtl_id', getValues('extraData.gtl_id'))
    }
  }, [musicTypes, getValues, setValue])

  return (
    <OfferCapabilityProvider capabilities={capabilities}>
      <div className={styles['artistic-info-inputs']}>
        <HasCapability name={FieldEnum.AUTHOR}>
          <ArtistField
            readOnly={false}
            artistType={ArtistType.AUTHOR}
            fieldArrayV2={artistFieldArray}
          />
        </HasCapability>
        <HasCapability name={FieldEnum.GENRE_MUSIC}>
          <Select
            label="Genre musical"
            options={musicTypesOptions}
            defaultOption={{
              label: 'Choisir un genre musical',
              value: DEFAULT_DESCRIPTION_FORM_VALUES.extraData.gtl_id,
            }}
            {...register('extraData.gtl_id', {
              disabled: readOnlyFields.includes('extraData.gtl_id'),
            })}
            required={mandatoryFields.includes(FieldEnum.GENRE_MUSIC)}
            error={errors.extraData?.gtl_id?.message}
          />
        </HasCapability>
        <HasCapability name={FieldEnum.PERFORMER}>
          <ArtistField
            readOnly={false}
            artistType={ArtistType.PERFORMER}
            fieldArrayV2={artistFieldArray}
          />
        </HasCapability>
      </div>
      <HasCapability name={FieldEnum.EAN}>
        <FormLayout.Row>
          <TextInput
            label="EAN-13 (European Article Numbering)"
            maxCharactersCount={13}
            {...register('extraData.ean', {
              disabled: readOnlyFields.includes('extraData.ean'),
            })}
            required={mandatoryFields.includes(FieldEnum.EAN)}
            error={errors.extraData?.ean?.message}
          />
        </FormLayout.Row>
      </HasCapability>
    </OfferCapabilityProvider>
  )
}
