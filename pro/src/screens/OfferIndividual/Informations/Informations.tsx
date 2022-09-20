import { FormikProvider, useFormik } from 'formik'
import type { FormikErrors } from 'formik'
import React, { useCallback } from 'react'
import { useHistory } from 'react-router-dom'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  createIndividualOffer,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import { ActionBar } from '../ActionBar'

import { filterCategories } from './utils'

export interface IInformationsProps {
  initialValues: IOfferIndividualFormValues
  readOnlyFields?: string[]
}

const Informations = ({
  initialValues,
  readOnlyFields = [],
}: IInformationsProps): JSX.Element => {
  const history = useHistory()
  const isCreation = useIsCreation()
  const {
    offerId,
    categories,
    subCategories,
    offererNames,
    venueList,
    reloadOffer,
  } = useOfferIndividualContext()

  const handleNextStep = async () => {
    formik.handleSubmit()
    if (formik.errors) redirectToError(formik.errors)
  }

  const redirectToError = useCallback(
    (errors: FormikErrors<IOfferIndividualFormValues>) => {
      if (errors) {
        const invalidElement = document.querySelector(
          `#${Object.keys(errors)[0]}`
        )
        if (invalidElement) {
          const scrollBehavior = doesUserPreferReducedMotion()
            ? 'auto'
            : 'smooth'
          invalidElement.scrollIntoView({
            behavior: scrollBehavior,
            block: 'center',
            inline: 'center',
          })
        }
      }
    },
    []
  )

  const onSubmit = async (formValues: IOfferIndividualFormValues) => {
    const { isOk, payload } =
      offerId === null
        ? await createIndividualOffer(formValues)
        : await updateIndividualOffer({ offerId, formValues })

    if (isOk) {
      await reloadOffer()
      history.push(
        isCreation
          ? `/offre/${payload.id}/v3/creation/individuelle/stocks`
          : `/offre/${payload.id}/v3/individuelle/stocks`
      )
    } else {
      formik.setErrors(payload.errors)
      redirectToError(formik.errors)
    }
    return Promise.resolve()
  }

  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  const initialVenue: TOfferIndividualVenue | undefined = venueList.find(
    venue => venue.id === initialValues.venueId
  )

  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    initialVenue
  )

  return (
    <FormikProvider value={formik}>
      <FormLayout small>
        <form onSubmit={formik.handleSubmit}>
          <OfferIndividualForm
            offererNames={offererNames}
            venueList={venueList}
            categories={filteredCategories}
            subCategories={filteredSubCategories}
            readOnlyFields={readOnlyFields}
          />
          <OfferFormLayout.ActionBar>
            <ActionBar onClickNext={handleNextStep} />
          </OfferFormLayout.ActionBar>
        </form>
      </FormLayout>
    </FormikProvider>
  )
}

export default Informations
