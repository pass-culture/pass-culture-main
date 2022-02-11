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
    case 'REMOVE_ONE_DEPARTMENT_FILTER': {
      const departmentValueToBeRemoved = action.value.departments
        ? action.value.departments[0].value
        : null
      const newDepartments = state.departments?.filter(
        department => department.value !== departmentValueToBeRemoved
      )
      return { ...state, departments: newDepartments }
    }
    case 'REMOVE_ONE_CATEGORY_FILTER': {
      const categoryValueToBeRemoved = action.value.categories
        ? action.value.categories[0].value
        : null
      const newCategories = state.categories?.filter(
        category => category.value !== categoryValueToBeRemoved
      )
      return { ...state, categories: newCategories }
    }
    case 'REMOVE_ONE_STUDENT_FILTER': {
      const studentValueToBeRemoved = action.value.students
        ? action.value.students[0].value
        : null
      const newStudents = state.students?.filter(
        student => student.value !== studentValueToBeRemoved
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
