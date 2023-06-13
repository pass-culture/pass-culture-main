import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import {
  INDIVIDUAL_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
} from 'core/Offers'
import {
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import CalendarCheckIcon from 'icons/ico-calendar-check.svg'
import CaseIcon from 'icons/ico-case.svg'
import DateIcon from 'icons/ico-date.svg'
import DuplicateOfferIcon from 'icons/ico-duplicate-offer.svg'
import NewOfferIcon from 'icons/ico-new-offer.svg'
import TemplateOfferIcon from 'icons/ico-template-offer.svg'
import VirtualEventIcon from 'icons/ico-virtual-event.svg'
import VirtualThingIcon from 'icons/ico-virtual-thing.svg'
import PhoneIcon from 'icons/stroke-info-phone.svg'
import ThingIcon from 'icons/stroke-thing.svg'
import { getFilteredCollectiveOffersAdapter } from 'pages/CollectiveOffers/adapters'
import { Banner } from 'ui-kit'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'
import Spinner from 'ui-kit/Spinner/Spinner'

import ActionsBar from './ActionsBar/ActionsBar'
import styles from './OfferType.module.scss'
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
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')
  const [isLoadingEligibility, setIsLoadingEligibility] = useState(false)
  const [isLoadingValidation, setIsLoadingValidation] = useState(false)
  const [isEligible, setIsEligible] = useState(false)
  const [isValidated, setIsValidated] = useState(true)

  useEffect(() => {
    const getTemplateCollectiveOffers = async () => {
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        collectiveOfferType: COLLECTIVE_OFFER_SUBTYPE.TEMPLATE.toLowerCase(),
        offererId: queryOffererId ? queryOffererId : 'all',
        venueId: queryVenueId ? queryVenueId : 'all',
      }
      const { isOk, message, payload } =
        await getFilteredCollectiveOffersAdapter(apiFilters)

      if (!isOk) {
        setHasCollectiveTemplateOffer(false)
        return notify.error(message)
      }

      if (payload.offers.length > 0) {
        setHasCollectiveTemplateOffer(true)
      }
    }
    const checkOffererEligibility = async () => {
      setIsLoadingEligibility(true)
      const offererNames = await api.listOfferersNames()

      const offererId =
        queryOffererId ?? offererNames.offerersNames[0].nonHumanizedId
      if (offererNames.offerersNames.length > 1 && !queryOffererId) {
        setIsEligible(true)
        setIsLoadingEligibility(false)
        return
      }

      if (offererId) {
        const { isOk, message, payload } =
          await canOffererCreateCollectiveOfferAdapter(Number(offererId))

        if (!isOk) {
          notify.error(message)
        }
        setIsEligible(payload.isOffererEligibleToEducationalOffer)
      }
      setIsLoadingEligibility(false)
    }
    const checkOffererValidation = async () => {
      setIsLoadingValidation(true)
      if (queryOffererId !== null) {
        const response = await api.getOfferer(Number(queryOffererId))
        setIsValidated(response.isValidated)
      }
      setIsLoadingValidation(false)
    }
    const initializeStates = async () => {
      await getTemplateCollectiveOffers()
      await checkOffererEligibility()
      await checkOffererValidation()
    }
    initializeStates()
  }, [queryOffererId, queryVenueId])

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
                  icon={PhoneIcon}
                  isChecked={values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  label="Au grand public"
                  onChange={handleChange}
                  value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  className={styles['offer-type-button']}
                />
                <RadioButtonWithImage
                  name="offerType"
                  icon={CaseIcon}
                  isChecked={values.offerType === OFFER_TYPES.EDUCATIONAL}
                  label="À un groupe scolaire"
                  onChange={handleChange}
                  value={OFFER_TYPES.EDUCATIONAL}
                  className={styles['offer-type-button']}
                />
              </FormLayout.Row>
            </FormLayout.Section>

            {isValidated &&
              values.offerType === OFFER_TYPES.EDUCATIONAL &&
              isEligible &&
              !isLoadingEligibility && (
                <FormLayout.Section
                  title="Quel est le type de l’offre ?"
                  className={styles['subtype-section']}
                >
                  <FormLayout.Row inline mdSpaceAfter>
                    <RadioButtonWithImage
                      name="collectiveOfferSubtype"
                      icon={CalendarCheckIcon}
                      isChecked={
                        values.collectiveOfferSubtype ===
                        COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE
                      }
                      label="Une offre réservable"
                      description="Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul."
                      onChange={handleChange}
                      value={COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE}
                    />
                  </FormLayout.Row>

                  <FormLayout.Row inline mdSpaceAfter>
                    <RadioButtonWithImage
                      name="collectiveOfferSubtype"
                      icon={TemplateOfferIcon}
                      isChecked={
                        values.collectiveOfferSubtype ===
                        COLLECTIVE_OFFER_SUBTYPE.TEMPLATE
                      }
                      label="Une offre vitrine"
                      description="Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé."
                      onChange={handleChange}
                      value={COLLECTIVE_OFFER_SUBTYPE.TEMPLATE}
                    />
                  </FormLayout.Row>
                </FormLayout.Section>
              )}
            {values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
              <FormLayout.Section
                title="Quel est le type de l’offre ?"
                className={styles['subtype-section']}
              >
                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    className={styles['individual-radio-button']}
                    name="individualOfferSubtype"
                    icon={ThingIcon}
                    isChecked={
                      values.individualOfferSubtype ===
                      INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
                    }
                    label="Un bien physique"
                    description="Livre, instrument de musique, abonnement, cartes et pass…"
                    onChange={handleChange}
                    value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}
                    dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}`}
                  />
                </FormLayout.Row>

                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    className={styles['individual-radio-button']}
                    name="individualOfferSubtype"
                    icon={VirtualThingIcon}
                    isChecked={
                      values.individualOfferSubtype ===
                      INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
                    }
                    label="Un bien numérique"
                    description="Ebook, jeu vidéo, abonnement streaming..."
                    onChange={handleChange}
                    value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}
                    dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}`}
                  />
                </FormLayout.Row>

                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    className={styles['individual-radio-button']}
                    name="individualOfferSubtype"
                    icon={DateIcon}
                    isChecked={
                      values.individualOfferSubtype ===
                      INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
                    }
                    label="Un évènement physique daté"
                    description="Concert, représentation, conférence, ateliers..."
                    onChange={handleChange}
                    value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}
                    dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}`}
                  />
                </FormLayout.Row>

                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    className={styles['individual-radio-button']}
                    name="individualOfferSubtype"
                    icon={VirtualEventIcon}
                    isChecked={
                      values.individualOfferSubtype ===
                      INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
                    }
                    label="Un évènement numérique daté"
                    description="Livestream, cours en ligne, conférence en ligne..."
                    onChange={handleChange}
                    value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
                    dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            )}

            {isEligible &&
              values.offerType === OFFER_TYPES.EDUCATIONAL &&
              values.collectiveOfferSubtype ===
                COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
                <FormLayout.Section
                  title="Créer une nouvelle offre ou dupliquer une offre ?"
                  className={styles['subtype-section']}
                >
                  <FormLayout.Row inline mdSpaceAfter>
                    <RadioButtonWithImage
                      name="collectiveOfferSubtypeDuplicate"
                      icon={NewOfferIcon}
                      isChecked={
                        values.collectiveOfferSubtypeDuplicate ===
                        COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER
                      }
                      label="Créer une nouvelle offre"
                      description="Créer une nouvelle offre réservable en partant d’un formulaire vierge."
                      onChange={handleChange}
                      value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER}
                    />
                  </FormLayout.Row>
                  <FormLayout.Row inline mdSpaceAfter>
                    <RadioButtonWithImage
                      name="collectiveOfferSubtypeDuplicate"
                      transparent
                      icon={DuplicateOfferIcon}
                      isChecked={
                        values.collectiveOfferSubtypeDuplicate ===
                        COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
                      }
                      label="Dupliquer les informations d’une d’offre vitrine"
                      description="Créez une offre réservable en dupliquant les informations d’une offre vitrine existante."
                      onChange={handleChange}
                      value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE}
                    />
                  </FormLayout.Row>
                </FormLayout.Section>
              )}

            {values.offerType === OFFER_TYPES.EDUCATIONAL &&
              (isLoadingEligibility || isLoadingValidation) && <Spinner />}
            {values.offerType === OFFER_TYPES.EDUCATIONAL && !isValidated && (
              <Banner>
                Votre structure est en cours de validation par les équipes pass
                Culture.
              </Banner>
            )}
            {values.offerType === OFFER_TYPES.EDUCATIONAL &&
              !isEligible &&
              !isLoadingEligibility && (
                <Banner
                  links={[
                    {
                      href: 'https://passculture.typeform.com/to/VtKospEg',
                      linkTitle: 'Faire une demande de référencement',
                    },
                    {
                      href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
                      linkTitle:
                        'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
                    },
                  ]}
                >
                  Pour proposer des offres à destination d’un groupe scolaire,
                  vous devez être référencé auprès du ministère de l’Éducation
                  Nationale et du ministère de la Culture.
                </Banner>
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
