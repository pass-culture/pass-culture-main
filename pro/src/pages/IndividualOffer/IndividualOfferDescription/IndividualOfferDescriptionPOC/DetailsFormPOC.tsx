import { Fragment } from 'react'
import { useFormContext } from 'react-hook-form'

import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
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

import type {
  NfdOfferFormField,
  NfdOfferFormSection,
} from '../components/NfdOfferForm/types'

type DetailsFormProps = {
  formDefinition: NfdOfferFormSection[]
}

const EMPTY_ACCESSIBILITY: AccessibilityFormValues = {
  visual: false,
  audio: false,
  motor: false,
  mental: false,
  none: false,
}

const isAccessibilityOption = (
  value: string
): value is keyof AccessibilityFormValues => value in EMPTY_ACCESSIBILITY

export const DetailsFormPOC = ({
  formDefinition,
}: DetailsFormProps): JSX.Element => {
  const {
    formState: { errors },
    register,
    setValue,
    watch,
  } = useFormContext<DetailsFormValues>()

  const renderField = (field: NfdOfferFormField): JSX.Element | null => {
    switch (field.type) {
      case 'TITLE':
        return (
          <FormLayout.Row>
            <TextInput
              maxCharactersCount={90}
              label={field.label}
              {...register('name')}
              error={errors.name?.message}
              required={field.required}
              autoComplete="false"
            />
          </FormLayout.Row>
        )
      case 'DESCRIPTION':
        return (
          <FormLayout.Row sideComponent={<MarkdownInfoBox />}>
            <TextArea
              label={field.label}
              maxLength={10000}
              {...register('description')}
              error={errors.description?.message}
            />
          </FormLayout.Row>
        )
      case 'BOOK_TYPE':
        return (
          <FormLayout.Row mdSpaceAfter>
            <Select
              {...register('showType', { onChange: noop })}
              label={field.label}
              required={field.required}
              options={field.options}
              defaultOption={{ label: 'Choisir un type de livre', value: '' }}
              value={watch('showType')}
            />
          </FormLayout.Row>
        )
      case 'BOOK_AUTHOR':
        return (
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label={field.label}
              maxLength={250}
              {...register('author')}
            />
          </FormLayout.Row>
        )
      case 'EAN':
        return (
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label={field.label}
              maxLength={250}
              {...register('ean')}
            />
          </FormLayout.Row>
        )
      case 'CULTURAL_OUTREACH':
        return (
          <FormLayout.Row mdSpaceAfter>
            <CheckboxGroup
              label={field.label}
              variant="detailed"
              error={errors.hasCulturalOutreachClaim?.message}
              options={[
                {
                  label: 'L’offre inclut une action de médiation spécifique',
                  description:
                    'Ex : rencontre avec des artistes, ateliers participatifs, comité de spectacteurs...',
                  checked: Boolean(watch('hasCulturalOutreachClaim')),
                  onChange: (event) =>
                    setValue('hasCulturalOutreachClaim', event.target.checked, {
                      shouldDirty: true,
                    }),
                },
              ]}
            />
          </FormLayout.Row>
        )
      case 'IMAGE_INPUT':
        return (
          <ImageDragAndDropUploader
            onImageUpload={noop}
            onImageDelete={noop}
            mode={UploaderModeEnum.OFFER}
            hideActionButtons
            onImageDropOrSelected={noop}
          />
        )
      case 'VIDEO_INPUT':
        return <VideoUploader uploadTipsId="" />
      case 'ACCESSIBILITY': {
        const accessibilityValues = {
          ...EMPTY_ACCESSIBILITY,
          ...watch('accessibility'),
        }

        return (
          <FormLayout.Row>
            <CheckboxGroup
              options={field.options.flatMap((option) => {
                if (!isAccessibilityOption(option.value)) {
                  return []
                }

                return [
                  {
                    label: option.label,
                    asset:
                      option.value === 'visual'
                        ? {
                            variant: 'icon' as const,
                            src: strokeAccessibilityEyeIcon,
                          }
                        : undefined,
                    sizing: 'fill' as const,
                    checked: accessibilityValues[option.value],
                    onChange: (event: React.ChangeEvent<HTMLInputElement>) =>
                      setValue(
                        'accessibility',
                        {
                          ...accessibilityValues,
                          [option.value]: event.target.checked,
                        },
                        { shouldDirty: true }
                      ),
                  },
                ]
              })}
              label={field.label}
              variant="detailed"
              error={errors.accessibility?.message}
            />
          </FormLayout.Row>
        )
      }
      default:
        return null
    }
  }

  return (
    <>
      {formDefinition.map((section) => (
        <FormLayout.Section key={section.id} title={section.title}>
          {section.fields.map((field) => (
            <Fragment key={field.type}>{renderField(field)}</Fragment>
          ))}
        </FormLayout.Section>
      ))}
    </>
  )
}
