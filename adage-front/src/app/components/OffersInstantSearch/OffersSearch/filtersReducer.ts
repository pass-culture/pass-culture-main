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
    case 'REMOVE_DEPARTMENTS_FILTER': {
      const departmentValuesToBeRemoved =
        action.value.departments?.map(department => department.value) || []
      const newDepartments = state.departments?.filter(
        department => !departmentValuesToBeRemoved.includes(department.value)
      )
      return { ...state, departments: newDepartments }
    }
    case 'REMOVE_CATEGORIES_FILTER': {
      const categoryValuesToBeRemoved =
        action.value.categories?.map(category => category.value) || []
      const newCategories = state.categories?.filter(
        category => !categoryValuesToBeRemoved.includes(category.value)
      )
      return { ...state, categories: newCategories }
    }
    case 'REMOVE_STUDENTS_FILTER': {
      const studentValuesToBeRemoved =
        action.value.students?.map(student => student.value) || []
      const newStudents = state.students?.filter(
        student => !studentValuesToBeRemoved.includes(student.value)
      )
      return { ...state, students: newStudents }
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
