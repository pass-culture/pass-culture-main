import { useFormikContext } from 'formik'
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

import {
  IOfferEducationalFormValues,
  IUserOfferer,
  Mode,
} from 'core/OfferEducational'
import { computeOffersUrl } from 'core/Offers/utils'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton, Banner } from 'ui-kit'

import { IOfferEducationalProps } from '../OfferEducational'
import buildSelectOptions from '../utils/buildSelectOptions'

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
  'onSubmit' | 'initialValues' | 'isEdition'
> & {
  mode: Mode
}

const OfferEducationalForm = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
  getIsOffererEligible,
  notify,
  mode,
}: IOfferEducationalFormProps): JSX.Element => {
  const [venuesOptions, setVenuesOptions] = useState<SelectOptions>([])
  const [currentOfferer, setCurrentOfferer] = useState<IUserOfferer | null>(
    null
  )
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

      setCurrentOfferer(selectedOfferer)
      setVenuesOptions(
        buildSelectOptions(
          selectedOfferer.managedVenues,
          'name',
          'id',
          'Sélectionner un lieu'
        )
      )
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
        mode={mode}
        userOfferers={userOfferers}
        venuesOptions={venuesOptions}
      />
      {isEligible && values.offererId && values.venueId ? (
        <>
          <FormOfferType
            categories={educationalCategories}
            subCategories={educationalSubCategories}
          />
          <FormEventAddress
            currentOfferer={currentOfferer}
            venuesOptions={venuesOptions}
          />
          <FormParticipants />
          <FormAccessibility />
          <FormContact />
          <FormNotifications />
        </>
      ) : null}
      <FormLayout.Actions>
        <Link className="secondary-link" to={computeOffersUrl({})}>
          Annuler et quitter
        </Link>
        <SubmitButton
          className="primary-button"
          disabled={!isEligible}
          isLoading={isLoading}
        >
          {mode === Mode.CREATION ? 'Étape suivante' : 'Enregistrer'}
        </SubmitButton>
      </FormLayout.Actions>
    </FormLayout>
  )
}

export default OfferEducationalForm
