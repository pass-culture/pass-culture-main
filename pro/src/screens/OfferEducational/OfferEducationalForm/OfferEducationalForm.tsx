import { useFormikContext } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import BannerPublicApi from 'components/Banner/BannerPublicApi'
import FormLayout from 'components/FormLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  OfferEducationalFormValues,
  isCollectiveOffer,
  Mode,
} from 'core/OfferEducational'
import { computeOffersUrl } from 'core/Offers/utils'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { Banner, ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { sortByLabel } from 'utils/strings'

import { OfferEducationalProps } from '../OfferEducational'

import FormAccessibility from './FormAccessibility'
import FormContact from './FormContact'
import FormImageUploader from './FormImageUploader'
import { ImageUploaderOfferProps } from './FormImageUploader/FormImageUploader'
import FormNotifications from './FormNotifications'
import FormOfferType from './FormOfferType'
import FormParticipants from './FormParticipants'
import FormPracticalInformation from './FormPracticalInformation'
import FormVenue from './FormVenue'
import styles from './OfferEducationalForm.module.scss'

type OfferEducationalFormProps = Omit<
  OfferEducationalProps,
  | 'offer'
  | 'setOffer'
  | 'initialValues'
  | 'isEdition'
  | 'getEducationalDomainsAdapter'
  | 'isOfferCancellable'
  | 'useOfferForFormValues'
> & {
  mode: Mode
  imageOffer: ImageUploaderOfferProps['imageOffer']
  onImageUpload: ImageUploaderOfferProps['onImageUpload']
  onImageDelete: ImageUploaderOfferProps['onImageDelete']
  isOfferCreated?: boolean
  offer?: CollectiveOffer | CollectiveOfferTemplate
}

const OfferEducationalForm = ({
  categories,
  userOfferers,
  getIsOffererEligible,
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
  const [isLoading, setIsLoading] = useState(false)
  const [isEligible, setIsEligible] = useState<boolean>()

  const { values, setFieldValue, initialValues } =
    useFormikContext<OfferEducationalFormValues>()

  const isDatesForTemplateOffer = useActiveFeature(
    'WIP_ENABLE_DATES_OFFER_TEMPLATE'
  )

  useScrollToFirstErrorAfterSubmit()

  const onOffererChange = useCallback(
    async (newOffererId: string) => {
      const selectedOfferer = userOfferers.find(
        (offerer) => offerer.id.toString() === newOffererId
      )

      if (selectedOfferer) {
        const checkOffererEligibilityToEducationalOffer = async () => {
          if (mode === Mode.EDITION || !getIsOffererEligible) {
            setIsEligible(true)
            return
          }

          setIsLoading(true)

          const { isOk, message, payload } = await getIsOffererEligible(
            selectedOfferer.id
          )

          if (isOk) {
            setIsEligible(payload.isOffererEligibleToEducationalOffer)
          }

          if (!isOk) {
            /* istanbul ignore next: TO FIX -> issue when trying to mock useNotification */
            notify.error(message)
          }

          setIsLoading(false)
        }

        await checkOffererEligibilityToEducationalOffer()

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
      }
    },
    [values.offererId, userOfferers, notify, getIsOffererEligible, mode]
  )

  useEffect(() => {
    void onOffererChange(values.offererId)
  }, [])

  return (
    <FormLayout className={styles['educational-form']} small>
      {isCollectiveOffer(offer) && offer.isPublicApi && (
        <BannerPublicApi className={styles['banner-space']}>
          Offre importée automatiquement
        </BannerPublicApi>
      )}
      <FormLayout.MandatoryInfo />

      {!isDatesForTemplateOffer && (
        <Banner
          className={styles['educational-form-banner']}
          type="notification-info"
        >
          Pour proposer plusieurs dates, heures ou prix, il vous sera nécessaire
          de <b>créer plusieurs offres</b>
        </Banner>
      )}

      <FormVenue
        isEligible={isEligible}
        mode={mode}
        isOfferCreated={isOfferCreated}
        userOfferers={userOfferers}
        venuesOptions={venuesOptions}
        categories={categories}
        onChangeOfferer={onOffererChange}
        offer={offer}
      />
      {isEligible && values.offererId && values.venueId ? (
        <>
          <FormOfferType
            categories={categories.educationalCategories}
            subCategories={categories.educationalSubCategories}
            domainsOptions={domainsOptions}
            nationalPrograms={nationalPrograms}
            disableForm={mode === Mode.READ_ONLY}
          />
          <FormImageUploader
            onImageDelete={onImageDelete}
            onImageUpload={onImageUpload}
            imageOffer={imageOffer}
          />
          <FormPracticalInformation
            currentOfferer={currentOfferer}
            venuesOptions={venuesOptions}
            disableForm={mode === Mode.READ_ONLY}
            isTemplate={isTemplate}
          />
          <FormParticipants
            disableForm={mode === Mode.READ_ONLY}
            isTemplate={isTemplate}
          />
          <FormAccessibility disableForm={mode === Mode.READ_ONLY} />
          <FormContact disableForm={mode === Mode.READ_ONLY} />
          <FormNotifications disableForm={mode === Mode.READ_ONLY} />
        </>
      ) : null}
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{ to: computeOffersUrl({}), isExternal: false }}
          >
            Annuler et quitter
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <SubmitButton
            disabled={!isEligible || mode === Mode.READ_ONLY}
            isLoading={isLoading}
          >
            {mode === Mode.CREATION ? 'Étape suivante' : 'Enregistrer'}
          </SubmitButton>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </FormLayout>
  )
}

export default OfferEducationalForm
