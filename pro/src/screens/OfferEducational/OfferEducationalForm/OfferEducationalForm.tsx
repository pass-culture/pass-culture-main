import { useFormikContext } from 'formik'
import { useCallback, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
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
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useNotification from 'hooks/useNotification'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { sortByLabel } from 'utils/strings'

import { OfferEducationalProps } from '../OfferEducational'

import FormAccessibility from './FormAccessibility'
import FormContact from './FormContact'
import FormDates from './FormDates/FormDates'
import FormImageUploader from './FormImageUploader'
import { ImageUploaderOfferProps } from './FormImageUploader/FormImageUploader'
import FormNotifications from './FormNotifications'
import FormOfferType from './FormOfferType'
import FormParticipants from './FormParticipants'
import FormPracticalInformation from './FormPracticalInformation'
import FormPriceDetails from './FormPriceDetails/FormPriceDetails'
import FormVenue from './FormVenue'
import styles from './OfferEducationalForm.module.scss'

export type OfferEducationalFormProps = Omit<
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
  const [isLoading, setIsLoading] = useState(false)
  const [isEligible, setIsEligible] = useState<boolean>()

  const { values, setFieldValue, initialValues } =
    useFormikContext<OfferEducationalFormValues>()

  useScrollToFirstErrorAfterSubmit()

  const onOffererChange = useCallback(
    async (newOffererId: string) => {
      const selectedOfferer = userOfferers.find(
        (offerer) => offerer.id.toString() === newOffererId
      )

      if (selectedOfferer) {
        const checkOffererEligibilityToEducationalOffer = async () => {
          if (mode === Mode.EDITION || mode === Mode.READ_ONLY) {
            setIsEligible(true)
            return
          }

          setIsLoading(true)

          try {
            const { canCreate } = await api.canOffererCreateEducationalOffer(
              selectedOfferer.id
            )
            setIsEligible(canCreate)
          } catch (error) {
            setIsEligible(false)
            notify.error(
              'Une erreur technique est survenue lors de la vérification de votre éligibilité.'
            )
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
    [values.offererId, userOfferers, notify, mode]
  )

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    onOffererChange(values.offererId)
  }, [])

  return (
    <>
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
            <FormContact disableForm={mode === Mode.READ_ONLY} />
            <FormNotifications disableForm={mode === Mode.READ_ONLY} />
          </>
        ) : null}
      </FormLayout>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{ to: '/offres/collectives', isExternal: false }}
          >
            Annuler et quitter
          </ButtonLink>
          <SubmitButton
            disabled={!isEligible || mode === Mode.READ_ONLY}
            isLoading={isLoading}
          >
            {mode === Mode.CREATION
              ? 'Étape suivante'
              : 'Enregistrer les modifications'}
          </SubmitButton>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}

export default OfferEducationalForm
