import { Label } from '@radix-ui/react-dropdown-menu'
import { Form, FormikProvider, useFormik } from 'formik'
import Autocomplete from 'react-google-autocomplete'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

// import { api } from 'apiClient/api'
import { api } from 'apiClient/api'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useNotification } from 'hooks/useNotification'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { ActionBar } from 'screens/IndividualOffer/ActionBar/ActionBar'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
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
  const notification = useNotification()
  const { t, i18n } = useTranslation('common')
  const navigate = useNavigate()

  const { offer } = useIndividualOfferContext()

  const initialValues = setDefaultInitialValues()
  const onSubmit = async (formValues: EuropeanFormFrontValues) => {
    try {
      console.log('formValues', formValues)

      // FIXME
      // So we dont send this to the api
      // as long as it doesnt support it.
      delete formValues['autoTranslate']

      const locale = i18n.language

      const { id } = await api.postEuropeanOffer({
        ...formValues,
        title: {
          [locale]: formValues.name,
        },
        description: {
          [locale]: formValues.description,
        },
        imageAlt: {
          [locale]: formValues.imageAlt,
        },
        date: `${formValues.date} 00:00:00`,
        latitude: formValues.latitude ?? 0,
        longitude: formValues.longitude ?? 0,
        price: formValues.price ?? 0,
        // autoTranslate: formValues.autoTranslate ?? false,
      })
      navigate(`/offre/individuelle/${id}/creation/confirmation`)
    } catch (err) {
      console.error(err)
      notification.error('An error occurred while creating the offer')
    }
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
              <Checkbox label={t('auto_translate')} name="autoTranslate" />
            </FormLayout.Row>
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
                onPlaceSelected={async (place) => {
                  const relevantAddressComponentKeysMap = [
                    'locality',
                    'country',
                    'street_number',
                    'route',
                    'postal_code',
                  ]

                  const res = place.address_components.reduce(
                    (acc: any, component: any) => {
                      const { types, long_name: value } = component
                      for (const t of types) {
                        if (relevantAddressComponentKeysMap.includes(t)) {
                          acc[t] = value
                          break
                        }
                      }

                      return acc
                    },
                    {
                      locality: '',
                      country: '',
                      street_number: '',
                      route: '',
                      postal_code: '',
                    }
                  )

                  const { lat, lng } = place.geometry.location
                  await formik.setValues({
                    ...formik.values,
                    city: res.locality,
                    country: res.country,
                    street: `${res.street_number}, ${res.route}`,
                    zipcode: res.postal_code,
                    latitude: lat(),
                    longitude: lng(),
                  })
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
                isOptional
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
