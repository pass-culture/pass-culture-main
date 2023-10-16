import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { SubcategoryIdEnum } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { getIndividualOfferVenuesAdapter } from 'core/Venue/adapters/getIndividualOfferVenuesAdapter'
import { getVenueAdapter } from 'core/Venue/adapters/getVenueAdapter'
import useCurrentUser from 'hooks/useCurrentUser'
import useNewIndividualOfferType from 'hooks/useNewIndividualOfferType'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioButton } from 'ui-kit'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

import { venueTypeSubcategoriesMapping } from './venueTypeSubcategoriesMapping'

const getVenueTypeAndSubcategories = async (
  venueId: string | null,
  offererId: string | null
): Promise<[string | null, OfferSubCategory[]]> => {
  let venueType: string | null = null
  let subcategories: OfferSubCategory[] = []

  if (venueId) {
    const [categoriesResponse, venueResponse] = await Promise.all([
      getCategoriesAdapter(),
      getVenueAdapter(Number(venueId)),
    ])

    if (venueResponse.isOk && categoriesResponse.isOk) {
      const venueData = venueResponse.payload
      const { subCategories } = categoriesResponse.payload
      venueType = venueData.venueType
      subcategories = subCategories
    }
  } else {
    const [categoriesResponse, venuesResponse] = await Promise.all([
      getCategoriesAdapter(),
      getIndividualOfferVenuesAdapter({
        offererId: offererId ? Number(offererId) : undefined,
      }),
    ])

    if (venuesResponse.isOk && categoriesResponse.isOk) {
      const { subCategories } = categoriesResponse.payload
      const venuesData = venuesResponse.payload.filter(
        venue => !venue.isVirtual
      )

      if (venuesData.length === 1) {
        venueType = venuesData[0].venueType
        subcategories = subCategories
      }
    }
  }
  return [venueType, subcategories]
}

const IndividualOfferType = (): JSX.Element | null => {
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()
  const [subcategories, setSubcategories] = useState<OfferSubCategory[]>([])
  const [venueType, setVenueType] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const queryParams = new URLSearchParams(location.search)
  const queryVenueId = queryParams.get('lieu')
  const queryOffererId = queryParams.get('structure')
  const isCategorySelectionActive = useNewIndividualOfferType()

  useEffect(() => {
    async function loadData() {
      // prevent admin from loading all venues
      const shouldLoadData =
        !currentUser.isAdmin || queryOffererId || queryVenueId

      if (isCategorySelectionActive && shouldLoadData) {
        setIsLoading(true)
        const [queriedVenueType, queriedSubcategories] =
          await getVenueTypeAndSubcategories(queryVenueId, queryOffererId)
        setVenueType(queriedVenueType)
        setSubcategories(queriedSubcategories)
        setIsLoading(false)
      }
    }
    void loadData()
  }, [queryVenueId, isCategorySelectionActive, queryOffererId])

  const venueTypeMostUsedSubcategories =
    venueType && venueTypeSubcategoriesMapping[venueType]

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      {isCategorySelectionActive && venueTypeMostUsedSubcategories && (
        <FormLayout.Section
          title="Quelle est la catégorie de l’offre ?"
          description="Ces catégories sont suggérées d’après les catégories les plus fréquemment sélectionnées pour votre type de lieu."
          className={styles['subcategory-section']}
        >
          <FormLayout.Row
            inline
            mdSpaceAfter
            className={styles['individual-radio-button-subcategory-group']}
          >
            {venueTypeMostUsedSubcategories.map(
              (subcategory: SubcategoryIdEnum) => (
                <RadioButton
                  className={styles['individual-radio-button-subcategory']}
                  key={subcategory}
                  withBorder
                  value={subcategory}
                  label={
                    subcategories.find(s => s.id === subcategory)?.proLabel ||
                    ''
                  }
                  name="individualOfferSubcategory"
                  variant={BaseRadioVariant.SECONDARY}
                />
              )
            )}
            <RadioButton
              className={styles['individual-radio-button-subcategory']}
              withBorder
              value="OTHER"
              label="Autre"
              name="individualOfferSubcategory"
              variant={BaseRadioVariant.SECONDARY}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}

      {(!venueTypeMostUsedSubcategories ||
        values.individualOfferSubcategory === 'OTHER') && (
        <FormLayout.Section
          title="Votre offre est :"
          className={styles['subtype-section']}
        >
          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              className={styles['individual-radio-button']}
              name="individualOfferSubtype"
              icon={thingStrokeIcon}
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
              icon={strokeVirtualThingIcon}
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
              icon={strokeDateIcon}
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
              icon={strokeVirtualEventIcon}
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
    </>
  )
}

export default IndividualOfferType
