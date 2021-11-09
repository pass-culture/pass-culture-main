import merge from 'lodash/merge'

import { SubCategory } from "custom_types/categories"

type SubCategoryExtend = Partial<SubCategory> & { id: string }

const categoryFactory = (subCategoryExtend: SubCategoryExtend): SubCategory => 
  merge(
    {},
    {
      categoryId: "CINEMA",
      matchingType: "EventType.CINEMA",
      proLabel: "Cinéma plein air",
      appLabel: "Cinéma plein air",
      searchGroupName: "CINEMA",
      isEvent: true,
      conditionalFields:  [
        "author",
        "visa",
        "stageDirector",
      ],
      canExpire: false,
      canBeDuo: true,
      canBeEducational: true,
      onlineOfflinePlatform: "OFFLINE",
      isDigitalDeposit: false,
      isPhysicalDeposit: false,
      reimbursementRule: "STANDARD",
      isSelectable: true,
    },
    subCategoryExtend
  )


export const subCategoriesFactory = (subCategoriesExtend: SubCategoryExtend[]): SubCategory[] => 
  subCategoriesExtend.map(categoryFactory)
