import { Label } from '@radix-ui/react-dropdown-menu'
import { Form, FormikProvider, useFormik } from 'formik'
import Autocomplete from 'react-google-autocomplete'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

// import { api } from 'apiClient/api'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { ActionBar } from 'screens/IndividualOffer/ActionBar/ActionBar'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { getToday } from 'utils/date'

import styles from './EuropeanOffer.module.scss'
import {
  setDefaultInitialValues,
  EuropeanFormFrontValues,
  validationSchema,
} from './utils'

export const EuropeanOffer = (): JSX.Element => {
  const { t, i18n } = useTranslation('common')
  const navigate = useNavigate()

  const { offer } = useIndividualOfferContext()

  const initialValues = setDefaultInitialValues()
  const onSubmit = (formValues: EuropeanFormFrontValues) => {
    console.log('onSubmit', formValues)
    // Submit
    /* try {
      const response = !offer
        ? await api.postDraftOffer(serializeDetailsPostData(formValues))
        : await api.patchDraftOffer(
            offer.id,
            serializeDetailsPatchData(formValues, !!offer.lastProvider)
          )

      const receivedOfferId = response.id
      await handleImageOnSubmit(receivedOfferId)
      await mutate([GET_OFFER_QUERY_KEY, receivedOfferId])

      // replace url to fix back button
      navigate(
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          offerId: receivedOfferId,
          mode,
        }),
        { replace: true }
      )
      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.DETAILS
          : OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerId: receivedOfferId,
        venueId: formik.values.venueId,
        offerType: 'individual',
        subcategoryId: formik.values.subcategoryId,
        choosenSuggestedSubcategory: formik.values.suggestedSubcategory,
      })
      navigate(
        getIndividualOfferUrl({
          offerId: receivedOfferId,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
        })
      )
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }
      for (const field in error.body) {
        formik.setFieldError(field, error.body[field])
      }
      // This is used from scroll to error
      formik.setStatus('apiError')
    }

    if (offer && formik.dirty) {
      notify.success(PATCH_SUCCESS_MESSAGE)
    } */
  }

  const formik = useFormik({
    initialValues,
    validationSchema,
    onSubmit,
  })

  const handlePreviousStepOrBackToReadOnly = () => navigate('/offre/creation')

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <h1 className={styles['title']}>{t('create_european_offer')}</h1>
          <ScrollToFirstErrorAfterSubmit />
          <FormLayout.MandatoryInfo />
          <FormLayout.Section title={t('about_your_offer')}>
            <FormLayout.Row>
              <TextInput
                countCharacters
                label={t('offer_title')}
                maxLength={90}
                name="name"
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextArea
                isOptional
                label={t('description')}
                maxLength={1000}
                name="description"
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <Label className={styles['label']}>{t('address')} *</Label>
              <Autocomplete
                className={styles['autocomplete-address']}
                language={i18n.language}
                apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}
                options={{ types: ['geocode'] }}
                onPlaceSelected={(place) => {
                  console.log(place)
                  console.log(place.geometry.location.lat())

                  /* const relevantAddressComponentKeysMap = {
                    'street_number': 'street',
                    'route': 'street',
                    'locality': 'city',
                    'country': 'country',
                    'postal_code': 'zipcode',
                  }
                  const { city, country, street, zipcode } =
                    place.address_components.reduce(
                      (acc, component) => {
                        const { types, long_name: value } = component
                        for (const t of types) {
                          if (Object.keys(relevantAddressComponentKeys).includes(t)) {
                            acc[relevantAddressComponentKeys[t]] = value
                            break
                          }
                        }
                      },
                      {
                        city: '',
                        country: '',
                        street: '',
                        zipcode: '',
                      }
                    )
                  const { lat: latitude, long: longitude } =
                    place.geometry.location
                  // Set city, country, street, latitude, longitude
                  // zipcode and currency
                  await formik.setValues({
                    ...formik.values,
                    city,
                    country,
                    street,
                    zipcode,
                    latitude,
                    longitude,
                  }) */
                }}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <DatePicker
                name="date"
                label={t('date')}
                isOptional
                hasLabelLineBreak={false}
                minDate={getToday()}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                label={t('external_url')}
                name="externalUrl"
                type="text"
                description={`${t('format')} : https://exemple.com`}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                label={t('image_url')}
                name="imageUrl"
                type="text"
                description={`${t('format')} : https://exemple.com`}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                isOptional
                label={t('image_description')}
                name="imageAlt"
                type="text"
                description={t('image_description_message')}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput
                name="price"
                label={t('price')}
                type="number"
                rightIcon={strokeEuroIcon}
                step="0.01"
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.DETAILS}
          isDisabled={
            formik.isSubmitting ||
            Boolean(offer && isOfferDisabled(offer.status))
          }
          dirtyForm={formik.dirty || offer === null}
        />
      </Form>
      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
