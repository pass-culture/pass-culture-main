import { useFormikContext } from 'formik'
import { useCallback, useEffect, useState } from 'react'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from 'components/Banner/BannerPublicApi'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import {
  isCollectiveOffer,
  Mode,
  OfferEducationalFormValues,
} from 'core/OfferEducational/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { SelectOption } from 'custom_types/form'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { sortByLabel } from 'utils/strings'

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
}

export const OfferEducationalForm = ({
  userOfferers,
  mode,
  domainsOptions,
  nationalPrograms,
  isTemplate,
  imageOffer,
  onImageUpload,
  onImageDelete,
  isOfferCreated = false,
  offer,
}: OfferEducationalFormProps): JSX.Element => {
  const notify = useNotification()

  const [venuesOptions, setVenuesOptions] = useState<SelectOption[]>([])
  const [currentOfferer, setCurrentOfferer] =
    useState<GetEducationalOffererResponseModel | null>(null)
  const [isEligible, setIsEligible] = useState<boolean>()

  const { values, setFieldValue, initialValues } =
    useFormikContext<OfferEducationalFormValues>()

  const isCustomContactFormEnabled = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT'
  )

  const onOffererChange = useCallback(
    async (newOffererId: string) => {
      const selectedOfferer = userOfferers.find(
        (offerer) => offerer.id.toString() === newOffererId
      )

      if (selectedOfferer) {
        const checkOffererEligibilityToEducationalOffer = () => {
          if (mode === Mode.EDITION || mode === Mode.READ_ONLY) {
            setIsEligible(true)
            return
          }
          setIsEligible(selectedOfferer.allowedOnAdage)
        }

        checkOffererEligibilityToEducationalOffer()

        let venuesOptions = selectedOfferer.managedVenues.map((item) => ({
          value: item['id'].toString(),
          label: item['name'] as string,
        }))
        if (venuesOptions.length > 1) {
          venuesOptions = [
            { value: '', label: 'Sélectionner un lieu' },
            ...sortByLabel(venuesOptions),
          ]
        }
        setCurrentOfferer(selectedOfferer)
        setVenuesOptions(venuesOptions)
        if (venuesOptions.length === 1) {
          await setFieldValue('venueId', venuesOptions[0].value)
        } else {
          await setFieldValue('venueId', initialValues.venueId)
        }
      } else {
        setIsEligible(false)
        setCurrentOfferer(null)
        setVenuesOptions([])
      }
    },
    [values.offererId, userOfferers, notify, mode]
  )

  useEffect(() => {
    if (values.offererId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      onOffererChange(values.offererId)
    }
  }, [values.offererId, userOfferers])

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
          userOfferers={userOfferers}
          venuesOptions={venuesOptions}
          onChangeOfferer={onOffererChange}
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
              currentOfferer={currentOfferer}
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
            {isCustomContactFormEnabled && isTemplate ? (
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
            link={{ to: computeCollectiveOffersUrl({}), isExternal: false }}
          >
            Annuler et quitter
          </ButtonLink>
          <Button
            type="submit"
            disabled={!isEligible || mode === Mode.READ_ONLY}
          >
            {mode === Mode.CREATION
              ? 'Étape suivante'
              : 'Enregistrer les modifications'}
          </Button>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}
