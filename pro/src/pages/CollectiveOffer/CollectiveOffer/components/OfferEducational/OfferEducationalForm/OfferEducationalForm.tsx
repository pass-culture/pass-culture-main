import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  Mode,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { sortByLabel } from 'commons/utils/strings'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from 'components/Banner/BannerPublicApi'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { OfferEducationalProps } from '../OfferEducational'

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
import { FormPriceDetails } from './FormPriceDetails/FormPriceDetails'
import { FormVenue } from './FormVenue/FormVenue'
import styles from './OfferEducationalForm.module.scss'

export type OfferEducationalFormProps = Omit<
  OfferEducationalProps,
  | 'offer'
  | 'setOffer'
  | 'initialValues'
  | 'isEdition'
  | 'isOfferCancellable'
  | 'useOfferForFormValues'
> & {
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

  const { values, setFieldValue, initialValues, dirty } =
    useFormikContext<OfferEducationalFormValues>()

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  useEffect(() => {
    async function handleOffererValues() {
      if (userOfferer) {
        if (mode === Mode.EDITION || mode === Mode.READ_ONLY) {
          setIsEligible(true)
        } else {
          setIsEligible(userOfferer.allowedOnAdage)
        }

        let venuesOptions = userOfferer.managedVenues.map((item) => ({
          value: item['id'].toString(),
          label: item['name'] as string,
        }))
        if (venuesOptions.length > 1) {
          venuesOptions = [
            {
              value: '',
              label: `Sélectionner ${isOfferAddressEnabled ? 'une structure' : 'un lieu'}`,
            },
            ...sortByLabel(venuesOptions),
          ]
        }
        setVenuesOptions(venuesOptions)
        if (venuesOptions.length === 1) {
          await setFieldValue('venueId', venuesOptions[0].value)
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
  }, [userOfferer])

  return (
    <>
      <ScrollToFirstErrorAfterSubmit />

      <FormLayout className={styles['educational-form']} fullWidthActions>
        {isCollectiveOffer(offer) && offer.isPublicApi && (
          <BannerPublicApi className={styles['banner-space']}>
            Offre importée automatiquement
          </BannerPublicApi>
        )}
        <FormLayout.MandatoryInfo />
        <FormVenue
          isEligible={isEligible}
          mode={mode}
          isOfferCreated={isOfferCreated}
          userOfferer={userOfferer}
          venuesOptions={venuesOptions}
          offer={offer}
        />
        {isEligible && values.offererId && values.venueId ? (
          <>
            <FormOfferType
              domainsOptions={domainsOptions}
              nationalPrograms={nationalPrograms}
              disableForm={mode === Mode.READ_ONLY}
            />
            <FormImageUploader
              onImageDelete={onImageDelete}
              onImageUpload={onImageUpload}
              imageOffer={imageOffer}
            />
            {isTemplate && (
              <FormDates
                disableForm={mode === Mode.READ_ONLY}
                dateCreated={offer?.dateCreated}
              />
            )}
            <FormPracticalInformation
              currentOfferer={userOfferer}
              venuesOptions={venuesOptions}
              disableForm={mode === Mode.READ_ONLY}
            />
            {isTemplate && (
              <FormPriceDetails disableForm={mode === Mode.READ_ONLY} />
            )}
            <FormParticipants
              disableForm={mode === Mode.READ_ONLY}
              isTemplate={isTemplate}
            />
            <FormAccessibility disableForm={mode === Mode.READ_ONLY} />
            {isTemplate ? (
              <FormContactTemplate disableForm={mode === Mode.READ_ONLY} />
            ) : (
              <FormContact disableForm={mode === Mode.READ_ONLY} />
            )}
            <FormNotifications disableForm={mode === Mode.READ_ONLY} />
          </>
        ) : null}
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
            disabled={!isEligible || mode === Mode.READ_ONLY || isSubmitting}
          >
            Enregistrer et continuer
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
