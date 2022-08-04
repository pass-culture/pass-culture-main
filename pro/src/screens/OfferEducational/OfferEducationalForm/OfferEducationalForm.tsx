import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import { IOfferEducationalFormValues, Mode } from 'core/OfferEducational'
import { computeOffersUrl } from 'core/Offers/utils'
import { SelectOption } from 'custom_types/form'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { Banner, SubmitButton } from 'ui-kit'

import { IOfferEducationalProps } from '../OfferEducational'

import FormAccessibility from './FormAccessibility'
import FormContact from './FormContact'
import FormEventAddress from './FormEventAddress'
import FormNotifications from './FormNotifications'
import FormOfferType from './FormOfferType'
import FormParticipants from './FormParticipants'
import FormVenue from './FormVenue'
import styles from './OfferEducationalForm.module.scss'

type IOfferEducationalFormProps = Omit<
  IOfferEducationalProps,
  'onSubmit' | 'initialValues' | 'isEdition' | 'getEducationalDomainsAdapter'
> & {
  mode: Mode
  domainsOptions: SelectOption[]
}

const OfferEducationalForm = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  getIsOffererEligible,
  notify,
  mode,
  domainsOptions,
}: IOfferEducationalFormProps): JSX.Element => {
  const [venuesOptions, setVenuesOptions] = useState<SelectOptions>([])
  const [currentOfferer, setCurrentOfferer] =
    useState<GetEducationalOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isEligible, setIsEligible] = useState<boolean>()

  const { values } = useFormikContext<IOfferEducationalFormValues>()

  useScrollToFirstErrorAfterSubmit()

  useEffect(() => {
    const selectedOfferer = userOfferers.find(
      offerer => offerer.id === values.offererId
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
          notify.error(message)
        }

        setIsLoading(false)
      }

      checkOffererEligibilityToEducationalOffer()

      let venuesOptions = selectedOfferer.managedVenues.map(item => ({
        value: item['id'] as string,
        label: item['name'] as string,
      }))
      if (venuesOptions.length > 1) {
        venuesOptions = [
          { value: '', label: 'Sélectionner un lieu' },
          ...venuesOptions,
        ]
      }
      setCurrentOfferer(selectedOfferer)
      setVenuesOptions(venuesOptions)
    }
  }, [values.offererId, userOfferers, notify, getIsOffererEligible, mode])
  return (
    <FormLayout className={styles['educational-form']} small>
      <p className={styles['educational-form-information']}>
        Tous les champs sont obligatoires sauf mention contraire.
      </p>

      <Banner
        className={styles['educational-form-banner']}
        type="notification-info"
      >
        Pour proposer plusieurs dates, heures ou prix, il vous sera nécessaire
        de <b>créer plusieurs offres</b>
      </Banner>

      <FormVenue
        isEligible={isEligible}
        disableForm={mode !== Mode.CREATION}
        userOfferers={userOfferers}
        venuesOptions={venuesOptions}
      />
      {isEligible && values.offererId && values.venueId ? (
        <>
          <FormOfferType
            categories={educationalCategories}
            subCategories={educationalSubCategories}
            domainsOptions={domainsOptions}
            disableForm={mode === Mode.READ_ONLY}
          />
          <FormEventAddress
            currentOfferer={currentOfferer}
            venuesOptions={venuesOptions}
            disableForm={mode === Mode.READ_ONLY}
          />
          <FormParticipants disableForm={mode === Mode.READ_ONLY} />
          <FormAccessibility disableForm={mode === Mode.READ_ONLY} />
          <FormContact disableForm={mode === Mode.READ_ONLY} />
          <FormNotifications disableForm={mode === Mode.READ_ONLY} />
        </>
      ) : null}
      <FormLayout.Actions>
        <Link className="secondary-link" to={computeOffersUrl({})}>
          Annuler et quitter
        </Link>
        <SubmitButton
          className="primary-button"
          disabled={!isEligible || mode === Mode.READ_ONLY}
          isLoading={isLoading}
        >
          {mode === Mode.CREATION ? 'Étape suivante' : 'Enregistrer'}
        </SubmitButton>
      </FormLayout.Actions>
    </FormLayout>
  )
}

export default OfferEducationalForm
