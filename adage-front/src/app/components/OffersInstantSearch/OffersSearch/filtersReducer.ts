import { Filters, Option } from 'app/types'

export type FiltersReducerAction = {
  type: string
  value: {
    departments?: Option[]
    categories?: Option<string[]>[]
    students?: Option[]
  }
}

export const filtersReducer = (
  state: Filters,
  action: FiltersReducerAction
): Filters => {
  switch (action.type) {
    case 'POPULATE_ALL_FILTERS':
      return {
        departments: action.value.departments ?? [],
        categories: action.value.categories ?? [],
        students: action.value.students ?? [],
      }
    case 'POPULATE_DEPARTMENTS_FILTER':
      return { ...state, departments: action.value.departments ?? [] }
    case 'POPULATE_CATEGORIES_FILTER':
      return { ...state, categories: action.value.categories ?? [] }
    case 'POPULATE_STUDENTS_FILTER':
      return { ...state, students: action.value.students ?? [] }
    case 'RESET_CURRENT_FILTERS':
      return { departments: [], categories: [], students: [] }
    default:
      return state
  }
}
