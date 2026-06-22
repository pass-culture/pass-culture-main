import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type GetCollectiveOfferResponseModel,
  type PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import { objectEntries, objectFromEntries } from '@/commons/utils/object'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { FormNotifications } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/OfferEducationalForm/FormNotifications/FormNotifications'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './CollectiveOfferInformationForm.module.scss'
import {
  type CollectiveOfferInformationFormValues,
  validationSchema,
} from './validationSchema'

export type CollectiveOfferInformationFormProps = {
  offer: GetCollectiveOfferResponseModel
  isCreation: boolean
  saveAndContinue: (
    partialOffer: PatchCollectiveOfferBodyModel
  ) => Promise<void>
  goBackLink: string
}

export const CollectiveOfferInformationForm = ({
  offer,
  isCreation,
  saveAndContinue,
  goBackLink,
}: CollectiveOfferInformationFormProps): JSX.Element => {
  const canEditDetails = offer.allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
  )

  const defaultValues: CollectiveOfferInformationFormValues = {
    bookingEmails:
      offer.bookingEmails.length > 0
        ? offer.bookingEmails?.map((email) => ({ email }))
        : [{ email: '' }],
    contactEmail: offer.contactEmail,
    contactPhone: offer.contactPhone,
    additionalDetails: offer.additionalDetails ?? '',
  }

  const form = useForm<CollectiveOfferInformationFormValues>({
    defaultValues,
    resolver: yupResolver(validationSchema),
  })

  const onSubmit = async (formValues: CollectiveOfferInformationFormValues) => {
    const partialOffer = objectFromEntries(
      objectEntries(form.formState.dirtyFields)
        .filter(([_, isDirty]) => isDirty)
        .map(([key, _]) => [key, formValues[key]])
    )

    if ('bookingEmails' in partialOffer) {
      partialOffer.bookingEmails = partialOffer.bookingEmails.map(
        ({ email }: Record<'email', string>) => email
      )
    }
    try {
      await saveAndContinue(partialOffer)
    } catch (e) {
      if (isErrorAPIError(e) && e.status < 500) {
        serializeApiErrors(e.body, form.setError)
      }
    }
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormLayout fullWidthActions>
          <FormLayout.MandatoryInfo />
          <FormNotifications disableForm={!canEditDetails} />
          <FormLayout.Section title="Comment les enseignants peuvent-ils vous contacter ?">
            <FormLayout.Row className={styles['phone-number-row']}>
              <PhoneNumberInput
                {...form.register('contactPhone')}
                disabled={!canEditDetails}
                error={form.formState.errors.contactPhone?.message}
                label="Téléphone"
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                {...form.register('contactEmail')}
                description="Format : email@exemple.com"
                disabled={!canEditDetails}
                error={form.formState.errors.contactEmail?.message}
                label="Email"
                required
                type="email"
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <FormLayout.Section title="Informations pratiques">
            <FormLayout.Row>
              <TextArea
                disabled={!canEditDetails}
                label={'Informations pratiques sur votre offre'}
                maxLength={MAX_PRICE_DETAILS_LENGTH}
                {...form.register('additionalDetails')}
                description={'Par exemple : Informations logistiques'}
                error={form.formState.errors.additionalDetails?.message}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>

        <ActionsBarSticky>
          <ActionsBarSticky.Left>
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              to={goBackLink}
              label={isCreation ? 'Retour' : 'Annuler et quitter'}
            />
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right
            dirtyForm={form.formState.isDirty || !offer}
            mode={isCreation ? Mode.CREATION : Mode.EDITION}
          >
            <Button
              type="submit"
              disabled={!canEditDetails || form.formState.isSubmitting}
              isLoading={form.formState.isSubmitting}
              label="Enregistrer et continuer"
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </form>

      <RouteLeavingGuardCollectiveOfferCreation
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </FormProvider>
  )
}
