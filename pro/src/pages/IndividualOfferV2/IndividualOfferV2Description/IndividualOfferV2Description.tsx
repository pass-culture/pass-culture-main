import { useState } from 'react'
import { FormProvider, useFieldArray, useForm } from 'react-hook-form'
import { Navigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { ArtistType, FieldEnum } from '@/apiClient/v1'
import { GET_CAPABILITIES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  HasCapability,
  OfferCapabilityProvider,
} from '@/commons/core/Offers/utils/offerCapabilityContext/offerCapabilityContext'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMusicTypes } from '@/commons/hooks/useMusicTypes'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import {
  CheckboxGroup,
  type CheckboxGroupOption,
} from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeLeftIcon from '@/icons/stroke-left.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/constants'
import { ArtistField } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/DetailsSubForm/components/ArtistField/ArtistField'
import { getFormV2ReadOnlyFields } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/utils'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/validationSchema'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

const IndividualOfferV2Description = (): JSX.Element => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const { nature, format } = useAppSelector((state) => state.nfd)

  const { data, isLoading } = useSWR(
    nature && format ? [GET_CAPABILITIES_QUERY_KEY, nature, format] : null,
    ([, natureParam, formatParam]) =>
      api.getCapabilities({
        query: { nature: natureParam, format: formatParam },
      })
  )
  const capabilities = data?.capabilities ?? []
  const mandatoryFields = data?.mandatoryFields ?? []

  // Form saving and validation done in next ticket
  const form = useForm<DetailsFormValues>({
    defaultValues: DEFAULT_DETAILS_FORM_VALUES,
  })
  const artistFieldArray = useFieldArray({
    control: form.control,
    name: 'artistOfferLinks',
  })

  const { musicTypes } = useMusicTypes()

  const musicTypesOptions = musicTypes.map((data) => ({
    value: data.gtl_id,
    label: data.label,
  }))

  // TODO create a component to handle all a11y options when there are more
  const [isLargePrint, setIsLargePrint] = useState(false)

  const accessibilityOptions: CheckboxGroupOption[] = [
    {
      label: 'Livre en gros caractères',
      asset: { variant: 'icon', src: strokeAccessibilityEyeIcon },
      sizing: 'fill',
      checked: isLargePrint,
      onChange: (event: React.ChangeEvent<HTMLInputElement>) =>
        setIsLargePrint(event.target.checked),
    },
  ]

  const readOnlyFields = getFormV2ReadOnlyFields(null, selectedPartnerVenue)

  if (!nature || !format) {
    return (
      <Navigate
        to="/offre/individuelle/v2/creation/nature-format-domaine"
        replace
      />
    )
  }

  if (isLoading) {
    return <Spinner />
  }

  return (
    <OfferCapabilityProvider capabilities={capabilities}>
      <FormProvider {...form}>
        <form>
          <MandatoryInfo />
          <FormLayout>
            <FormLayout.Section title="À propos de votre offre">
              <HasCapability name={FieldEnum.TITLE}>
                <FormLayout.Row>
                  <TextInput
                    name="title"
                    maxCharactersCount={90}
                    label="Titre du bien"
                    // All register and error handling done in next ticket
                    // {...register('name')}
                    // error={errors.name?.message}
                    required={mandatoryFields.includes(FieldEnum.TITLE)}
                    autoComplete="false"
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.DESCRIPTION}>
                <FormLayout.Row>
                  <TextArea
                    label="Description"
                    description='Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_. Vous pourrez vérifier l’affichage à l’étape "Aperçu".'
                    name="description"
                    maxLength={10000}
                    required={mandatoryFields.includes(FieldEnum.DESCRIPTION)}
                    // {...form.register('description')}
                    disabled={readOnlyFields.includes('description')}
                    // error={form.formState.errors.description?.message}
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.AUTHOR}>
                <FormLayout.Row lgSpaceAfter>
                  <ArtistField
                    readOnly={false}
                    artistType={ArtistType.AUTHOR}
                    fieldArray={artistFieldArray}
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.GENRE_MUSIC}>
                <FormLayout.Row lgSpaceAfter>
                  <Select
                    label="Genre musical"
                    name="Genre musical"
                    options={musicTypesOptions}
                    required={mandatoryFields.includes(FieldEnum.GENRE_MUSIC)}
                    defaultOption={{
                      label: 'Choisir un genre musical',
                      value: DEFAULT_DETAILS_FORM_VALUES.gtl_id,
                    }}
                    disabled={readOnlyFields.includes('gtl_id')}
                    // {...register('gtl_id')}
                    // error={errors.gtl_id?.message}
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.PERFORMER}>
                <FormLayout.Row lgSpaceAfter>
                  <ArtistField
                    readOnly={false}
                    artistType={ArtistType.PERFORMER}
                    fieldArray={artistFieldArray}
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.EAN}>
                <FormLayout.Row>
                  <TextInput
                    label="EAN-13 (European Article Numbering)"
                    name="EAN"
                    required={mandatoryFields.includes(FieldEnum.EAN)}
                    maxCharactersCount={13}
                    disabled={readOnlyFields.includes('ean')}
                    // {...register('ean')}
                    // error={errors.ean?.message}
                  />
                </FormLayout.Row>
              </HasCapability>
            </FormLayout.Section>
            <HasCapability name={FieldEnum.ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT}>
              <FormLayout.Section title="Modalités d'accessibilité">
                <FormLayout.Row>
                  <CheckboxGroup
                    options={accessibilityOptions}
                    disabled={readOnlyFields.includes('accessibility')}
                    label="Sélectionnez le dispositif d'accessibilité qui correspond à votre offre :"
                    description="Sélectionnez au moins une option"
                    variant="detailed"
                    error={form.formState.errors.accessibility?.message}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            </HasCapability>
            <HasCapability name={FieldEnum.IMAGE}>
              <FormLayout.Section title="Illustrez votre offre">
                <FormLayout.Row>
                  <ImageDragAndDropUploader
                    // TODO : use new UploadZone when design PR is merged
                    onImageUpload={noop}
                    onImageDelete={noop}
                    mode={UploaderModeEnum.OFFER}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            </HasCapability>
          </FormLayout>
        </form>
      </FormProvider>

      <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
        <ActionsBarSticky.Left>
          <Button
            as="router-link"
            color={ButtonColor.NEUTRAL}
            variant={ButtonVariant.SECONDARY}
            to="/offre/individuelle/v2/creation/nature-format-domaine"
            label="Étape précédente"
            icon={strokeLeftIcon}
            iconPosition={IconPositionEnum.LEFT}
          />
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button
            color={ButtonColor.BRAND}
            variant={ButtonVariant.PRIMARY}
            label="Étape suivante"
            icon={strokeRightIcon}
            iconPosition={IconPositionEnum.RIGHT}
          />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </OfferCapabilityProvider>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2Description
