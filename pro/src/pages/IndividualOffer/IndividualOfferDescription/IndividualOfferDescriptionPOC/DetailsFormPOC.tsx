import { useFormContext } from 'react-hook-form'

import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { VideoUploader } from '@/components/VideoUploader/VideoUploader'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import {
  HasCapability,
  OfferCapabilityProvider,
} from '../components/NfdOfferForm/OfferCapabilityContext'

type DetailsFormProps = {
  mandatoryFields: string[]
  capabilities: string[]
}

export const DetailsFormPOC = ({
  mandatoryFields,
  capabilities,
}: DetailsFormProps): JSX.Element => {
  const {
    formState: { errors },
    register,
    setValue,
    watch,
  } = useFormContext<DetailsFormValues>()
  const accessibility = watch('accessibility')

  const accessibilityOptions = updateAccessibilityField(setValue, accessibility)

  // using showType for example
  const bookType = watch('showType')

  return (
    <OfferCapabilityProvider capabilities={capabilities}>
      <FormLayout.Section title="À propos de votre offre">
        <HasCapability name="TITLE">
          <FormLayout.Row>
            <TextInput
              maxCharactersCount={90}
              label="Titre de l’offre"
              {...register('name')}
              error={errors.name?.message}
              required
              // This is so browsers don't raise any issue / improvement
              // regarding the existence of an <input type="text" name="name" />
              // that isnt about an user's name to be autofilled.
              autoComplete="false"
            />
          </FormLayout.Row>
        </HasCapability>
        <HasCapability name="DESCRIPTION">
          <FormLayout.Row sideComponent={<MarkdownInfoBox />}>
            <TextArea
              label="Description"
              maxLength={10000}
              {...register('description')}
              error={errors.description?.message}
            />
          </FormLayout.Row>
        </HasCapability>
        <HasCapability name="BOOK_DETAILS">
          <FormLayout.Row mdSpaceAfter>
            <Select
              // using showType for example
              {...register('showType', {
                onChange: noop,
              })}
              label="Type de livre"
              required={mandatoryFields.includes('BOOK_TYPE')}
              options={[
                {
                  value: 'BD',
                  label: 'Bande dessinée',
                },
                {
                  value: 'Roman',
                  label: 'Roman',
                },
                { value: 'Manga', label: 'Manga' },
              ]}
              defaultOption={{
                label: 'Choisir un type de livre',
                value: '',
              }}
              value={bookType}
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <TextInput label="Auteur" maxLength={250} {...register('author')} />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="EAN-13 (European Article Numbering"
              maxLength={250}
              {...register('ean')}
            />
          </FormLayout.Row>
        </HasCapability>
        <HasCapability name="CULTURAL_OUTREACH">
          <FormLayout.Row mdSpaceAfter>
            <CheckboxGroup
              label="Action de médiation"
              variant="detailed"
              error={errors.hasCulturalOutreachClaim?.message}
              options={[
                {
                  label: 'L’offre inclut une action de médiation spécifique',
                  description:
                    'Ex : rencontre avec des artistes, ateliers participatifs, comité de spectacteurs...',
                  checked: Boolean(watch('hasCulturalOutreachClaim')),
                  onChange: (e) =>
                    setValue('hasCulturalOutreachClaim', e.target.checked, {
                      shouldDirty: true,
                    }),
                },
              ]}
            />
          </FormLayout.Row>
        </HasCapability>
      </FormLayout.Section>
      <FormLayout.Section title="Illustrez votre offre">
        <HasCapability name="IMAGE_INPUT">
          <ImageDragAndDropUploader
            onImageUpload={noop}
            onImageDelete={noop}
            mode={UploaderModeEnum.OFFER}
            hideActionButtons
            onImageDropOrSelected={noop}
          />
        </HasCapability>
        <HasCapability name="VIDEO_INPUT">
          <VideoUploader uploadTipsId={''} />
        </HasCapability>
      </FormLayout.Section>
      <HasCapability name="ACCESSIBILITY">
        {accessibilityOptions && (
          <FormLayout.Section title="Modalités d’accessibilité">
            <FormLayout.Row>
              <CheckboxGroup
                options={[
                  {
                    label: 'Livre en gros caractères',
                    asset: { variant: 'icon', src: strokeAccessibilityEyeIcon },
                    sizing: 'fill',
                    checked: Boolean(accessibility?.visual),
                    onChange: undefined,
                  },
                ]}
                label="Sélectionner l'option si votre offre correspond :"
                variant="detailed"
                error={errors.accessibility?.message}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}
      </HasCapability>
    </OfferCapabilityProvider>
  )
}
