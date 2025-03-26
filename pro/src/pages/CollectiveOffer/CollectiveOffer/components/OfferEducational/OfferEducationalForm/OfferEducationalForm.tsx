import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  Mode,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { SelectOption } from 'commons/custom_types/form'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { sortByLabel } from 'commons/utils/strings'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from 'components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import { DomainOption } from '../useOfferEducationalFormData'

import { FormAccessibility } from './FormAccessibility/FormAccessibility'
import { FormContact } from './FormContact/FormContact'
import { FormContactTemplate } from './FormContactTemplate/FormContactTemplate'
import { FormDates } from './FormDates/FormDates'
import {
  FormImageUploader,
  ImageUploaderOfferProps,
} from './FormImageUploader/FormImageUploader'
import { FormNotifications } from './FormNotifications/FormNotifications'
import { FormOfferType } from './FormOfferType/FormOfferType'
import { FormParticipants } from './FormParticipants/FormParticipants'
import { FormPracticalInformation } from './FormPracticalInformation/FormPracticalInformation'
import { FormVenue } from './FormVenue/FormVenue'
import styles from './OfferEducationalForm.module.scss'

export type OfferEducationalFormProps = {
  userOfferer: GetEducationalOffererResponseModel | null
  domainsOptions: DomainOption[]
  nationalPrograms: SelectOption<number>[]
  isTemplate: boolean
  mode: Mode
  imageOffer: ImageUploaderOfferProps['imageOffer']
  onImageUpload: ImageUploaderOfferProps['onImageUpload']
  onImageDelete: ImageUploaderOfferProps['onImageDelete']
  isOfferCreated?: boolean
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  isSubmitting: boolean
}

export const OfferEducationalForm = ({
  userOfferer,
  mode,
  domainsOptions,
  nationalPrograms,
  isTemplate,
  imageOffer,
  onImageUpload,
  onImageDelete,
  isOfferCreated = false,
  offer,
  isSubmitting,
}: OfferEducationalFormProps): JSX.Element => {
  const [venuesOptions, setVenuesOptions] = useState<SelectOption[]>([])
  const [isEligible, setIsEligible] = useState<boolean>()

  const { setFieldValue, initialValues, dirty, values } =
    useFormikContext<OfferEducationalFormValues>()

  const { data: selectedOfferer } = useOfferer(userOfferer?.id)

  const canEditDetails =
    !offer ||
    isActionAllowedOnCollectiveOffer(
      offer,
      isCollectiveOffer(offer)
        ? CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
        : CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS
    )

  useEffect(() => {
    async function handleOffererValues() {
      if (userOfferer) {
        if (mode === Mode.EDITION || mode === Mode.READ_ONLY) {
          setIsEligible(true)
        } else {
          setIsEligible(userOfferer.allowedOnAdage)
        }

        let newVenuesOptions = userOfferer.managedVenues.map((item) => ({
          value: item['id'].toString(),
          label: item['name'] as string,
        }))
        if (newVenuesOptions.length > 1) {
          newVenuesOptions = [
            {
              value: '',
              label: `Sélectionner une structure`,
            },
            ...sortByLabel(newVenuesOptions),
          ]
        }
        setVenuesOptions(newVenuesOptions)
        if (newVenuesOptions.length === 1) {
          await setFieldValue('venueId', newVenuesOptions[0].value)
        } else {
          await setFieldValue('venueId', initialValues.venueId)
        }
      } else {
        setIsEligible(false)
        setVenuesOptions([])
      }
    }

    // as the call is async, it can create refresh issues.
    // This is to prevent these issues
    setTimeout(() => {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      handleOffererValues()
    })
  }, [userOfferer?.id])

  return (
    <>
      <ScrollToFirstErrorAfterSubmit />

      <FormLayout className={styles['educational-form']} fullWidthActions>
        {isCollectiveOffer(offer) && offer.isPublicApi && (
          <BannerPublicApi className={styles['banner-space']}>
            Offre importée automatiquement
          </BannerPublicApi>
        )}
        {!selectedOfferer?.allowedOnAdage ? (
          <Callout
            variant={CalloutVariant.INFO}
            className={styles['no-offerer-callout']}
          >
            Vous ne pouvez pas créer d’offre collective tant que votre entité
            juridique n’est pas validée.
          </Callout>
        ) : (
          <>
            <FormLayout.MandatoryInfo />
            {venuesOptions.length > 1 && (
              <FormVenue
                isEligible={isEligible}
                disableForm={!canEditDetails}
                isOfferCreated={isOfferCreated}
                userOfferer={userOfferer}
                venuesOptions={venuesOptions}
                offer={offer}
              />
            )}
            {values.offererId && values.venueId && isEligible ? (
              <>
                <FormOfferType
                  domainsOptions={domainsOptions}
                  disableForm={!canEditDetails}
                  isTemplate={isTemplate}
                />
                <FormImageUploader
                  onImageDelete={onImageDelete}
                  onImageUpload={onImageUpload}
                  imageOffer={imageOffer}
                  disableForm={!canEditDetails}
                  isTemplate={isTemplate}
                />
                {isTemplate && (
                  <FormDates
                    disableForm={!canEditDetails}
                    dateCreated={offer?.dateCreated}
                  />
                )}
                <FormPracticalInformation
                  currentOfferer={userOfferer}
                  venuesOptions={venuesOptions}
                  disableForm={!canEditDetails}
                />
                <FormParticipants disableForm={!canEditDetails} />
                <FormAccessibility disableForm={!canEditDetails} />
                {isTemplate ? (
                  <FormContactTemplate disableForm={!canEditDetails} />
                ) : (
                  <FormContact disableForm={!canEditDetails} />
                )}
                <FormNotifications disableForm={!canEditDetails} />
              </>
            ) : null}
          </>
        )}
      </FormLayout>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            to={computeCollectiveOffersUrl({})}
          >
            Annuler et quitter
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right dirtyForm={dirty || !offer} mode={mode}>
          <Button
            type="submit"
            disabled={!isEligible || !canEditDetails || isSubmitting}
          >
            Enregistrer et continuer
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
