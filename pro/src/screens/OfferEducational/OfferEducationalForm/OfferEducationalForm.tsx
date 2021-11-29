import { useFormikContext } from 'formik'
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import {
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'
import { CGU_URL } from 'utils/config'

import { IOfferEducationalProps } from '../OfferEducational'
import buildSelectOptions from '../utils/buildSelectOptions'

import FormAccessibility from './FormAccessibility'
import FormCategory from './FormCategory'
import FormContact from './FormContact'
import FormEventAddress from './FormEventAddress'
import FormNotifications from './FormNotifications'
import FormParticipants from './FormParticipants'
import FormVenue from './FormVenue'
import styles from './OfferEducationalForm.module.scss'

type IOfferEducationalFormProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalForm = ({
  educationalCategories,
  educationalSubCategories,
  userOfferers,
}: IOfferEducationalFormProps): JSX.Element => {
  const [venuesOptions, setVenuesOptions] = useState<SelectOptions>([])
  const [currentOfferer, setCurrentOfferer] = useState<IUserOfferer | null>(
    null
  )
  const { values } = useFormikContext<IOfferEducationalFormValues>()

  useEffect(() => {
    const selectedOfferer = userOfferers.find(
      offerer => offerer.id === values.offererId
    )
    if (selectedOfferer) {
      setCurrentOfferer(selectedOfferer)
      setVenuesOptions(
        buildSelectOptions(
          selectedOfferer.managedVenues,
          'name',
          'id',
          'Séléctionner un lieu'
        )
      )
    }
  }, [values.offererId, userOfferers])

  return (
    <FormLayout className={styles['educational-form']} small>
      <p className={styles['educational-form-information']}>
        Tous les champs sont obligatoires sauf mention contraire.
      </p>
      <FormCategory
        categories={educationalCategories}
        subCategories={educationalSubCategories}
      />
      <FormVenue userOfferers={userOfferers} venuesOptions={venuesOptions} />
      <FormEventAddress
        currentOfferer={currentOfferer}
        venuesOptions={venuesOptions}
      />
      <FormParticipants />
      <FormAccessibility />
      <FormContact />
      <FormNotifications />
      <Banner
        href={CGU_URL}
        linkTitle="Consulter les Conditions Générales d’Utilisation"
        type="notification-info"
      />
      <FormLayout.Actions>
        <Link className="secondary-link" to={computeOffersUrl({})}>
          Annuler et quitter
        </Link>
        <SubmitButton
          className="primary-button"
          disabled={false}
          isLoading={false}
        >
          Étape suivante
        </SubmitButton>
      </FormLayout.Actions>
    </FormLayout>
  )
}

export default OfferEducationalForm
