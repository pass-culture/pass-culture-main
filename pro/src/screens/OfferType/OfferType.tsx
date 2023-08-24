import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
} from 'core/Offers/constants'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import strokeProfIcon from 'icons/stroke-prof.svg'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'

import ActionsBar from './ActionsBar/ActionsBar'
import styles from './OfferType.module.scss'
import OfferTypeEducational from './OfferTypeEducational/OfferTypeEducational'
import OfferTypeIndividual from './OfferTypeIndividual/OfferTypeIndividual'
import { OfferTypeFormValues } from './types'

const OfferType = (): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const initialValues: OfferTypeFormValues = {
    offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
    collectiveOfferSubtypeDuplicate:
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
    individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
  }

  const [hasCollectiveTemplateOffer, setHasCollectiveTemplateOffer] =
    useState(false)
  const [isEligible, setIsEligible] = useState(false)

  const getNextPageHref = (values: OfferTypeFormValues) => {
    if (values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerType: values.individualOfferSubtype,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        from: OFFER_FORM_HOMEPAGE,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      })

      /* istanbul ignore next: condition will be removed when FF active in prod */
      return navigate({
        pathname: getOfferIndividualUrl({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        search: `${location.search}${location.search ? '&' : '?'}offer-type=${
          values.individualOfferSubtype
        }`,
      })
    }
    // Offer type is EDUCATIONAL
    if (values.collectiveOfferSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE) {
      return navigate({
        pathname: '/offre/creation/collectif/vitrine',
        search: location.search,
      })
    }
    if (
      values.collectiveOfferSubtypeDuplicate ===
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
    ) {
      if (!hasCollectiveTemplateOffer) {
        return notify.error(
          'Vous devez créer une offre vitrine avant de pouvoir utiliser cette fonctionnalité'
        )
      }

      return navigate({
        pathname: '/offre/creation/collectif/selection',
        search: location.search,
      })
    }

    return navigate({
      pathname: '/offre/creation/collectif',
      search: location.search,
    })
  }

  const formik = useFormik<OfferTypeFormValues>({
    initialValues: initialValues,
    onSubmit: getNextPageHref,
  })
  const { values, handleChange } = formik

  return (
    <div className={styles['offer-type-container']}>
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <FormLayout.Section title="À qui destinez-vous cette offre ?">
              <FormLayout.Row inline>
                <RadioButtonWithImage
                  name="offerType"
                  icon={phoneStrokeIcon}
                  isChecked={values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  label="Au grand public"
                  onChange={handleChange}
                  value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  className={styles['offer-type-button']}
                />
                <RadioButtonWithImage
                  name="offerType"
                  icon={strokeProfIcon}
                  isChecked={values.offerType === OFFER_TYPES.EDUCATIONAL}
                  label="À un groupe scolaire"
                  onChange={handleChange}
                  value={OFFER_TYPES.EDUCATIONAL}
                  className={styles['offer-type-button']}
                />
              </FormLayout.Row>
            </FormLayout.Section>

            {values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
              <OfferTypeIndividual />
            )}

            {values.offerType === OFFER_TYPES.EDUCATIONAL && (
              <OfferTypeEducational
                setHasCollectiveTemplateOffer={setHasCollectiveTemplateOffer}
                setIsEligible={setIsEligible}
                isEligible={isEligible}
              />
            )}
            <ActionsBar
              disableNextButton={
                values.offerType === OFFER_TYPES.EDUCATIONAL && !isEligible
              }
            />
          </FormLayout>
        </form>
      </FormikProvider>
    </div>
  )
}

export default OfferType
