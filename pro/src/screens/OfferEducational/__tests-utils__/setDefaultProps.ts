import { categoriesFactory } from "screens/OfferEducational/__tests-utils__/categoryFactory"
import { subCategoriesFactory } from "screens/OfferEducational/__tests-utils__/subCategoryFactory"

import { IOfferEducationalProps } from "../OfferEducational"

const mockEducationalCategories = categoriesFactory(
  [
    {
      id: "MUSEE",
      proLabel: "Musée, patrimoine, architecture, arts visuels",
    },
    {
      id: "CINEMA",
      proLabel: "Cinéma",
    }
  ]
)

const mockEducationalSubcategories = subCategoriesFactory(
  [
    {
      id: "CINE_PLEIN_AIR",
      categoryId: "CINEMA",
      proLabel: "Cinéma plein air",
    },
    {
      id: "EVENEMENT_CINE",
      categoryId: "CINEMA",
      proLabel: "Événement cinématographique",
    },
    {
      id: "VISITE_GUIDEE",
      categoryId: "MUSEE",
      proLabel: "Visite guidée",
    }
  ]
)

const defaultProps = (): IOfferEducationalProps => ({
  initialValues: {},
  educationalCategories: mockEducationalCategories,
  educationalSubcategories: mockEducationalSubcategories,
})

export default defaultProps
