import { Filters, Option } from 'app/types'

type PopulateAllFiltersAction = {
  type: 'POPULATE_ALL_FILTERS'
  allFilters: {
    departments: Option[]
    categories: Option<string[]>[]
    students: Option[]
  }
}

type ResetCurrentFiltersAction = {
  type: 'RESET_CURRENT_FILTERS'
}

type PopulateDepartmentsFilterAction = {
  type: 'POPULATE_DEPARTMENTS_FILTER'
  departmentFilters: Option[]
}

type PopulateCategoriesFilterAction = {
  type: 'POPULATE_CATEGORIES_FILTER'
  categoryFilters: Option<string[]>[]
}

type PopulateStudentsFilterAction = {
  type: 'POPULATE_STUDENTS_FILTER'
  studentFilters: Option[]
}

type RemoveDepartmentFilterAction = {
  type: 'REMOVE_ONE_DEPARTMENT_FILTER'
  departmentFilter: Option
}

type RemoveCategoryFilterAction = {
  type: 'REMOVE_ONE_CATEGORY_FILTER'
  categoryFilter: Option<string[]>
}

type RemoveStudentFilterAction = {
  type: 'REMOVE_ONE_STUDENT_FILTER'
  studentFilter: Option
}

export type FiltersReducerAction =
  | PopulateAllFiltersAction
  | ResetCurrentFiltersAction
  | PopulateDepartmentsFilterAction
  | PopulateCategoriesFilterAction
  | PopulateStudentsFilterAction
  | RemoveDepartmentFilterAction
  | RemoveCategoryFilterAction
  | RemoveStudentFilterAction

export const filtersReducer = (
  state: Filters,
  action: FiltersReducerAction
): Filters => {
  switch (action.type) {
    case 'POPULATE_ALL_FILTERS':
      return {
        departments: action.allFilters.departments,
        categories: action.allFilters.categories,
        students: action.allFilters.students,
      }
    case 'REMOVE_ONE_DEPARTMENT_FILTER': {
      const newDepartments = state.departments?.filter(
        department => department.value !== action.departmentFilter.value
      )
      return { ...state, departments: newDepartments }
    }
    case 'REMOVE_ONE_CATEGORY_FILTER': {
      const newCategories = state.categories?.filter(
        category => category.value !== action.categoryFilter.value
      )
      return { ...state, categories: newCategories }
    }
    case 'REMOVE_ONE_STUDENT_FILTER': {
      const newStudents = state.students?.filter(
        student => student.value !== action.studentFilter.value
      )
      return { ...state, students: newStudents }
    }
    case 'POPULATE_DEPARTMENTS_FILTER':
      return { ...state, departments: action.departmentFilters }
    case 'POPULATE_CATEGORIES_FILTER':
      return { ...state, categories: action.categoryFilters }
    case 'POPULATE_STUDENTS_FILTER':
      return { ...state, students: action.studentFilters }
    case 'RESET_CURRENT_FILTERS':
      return { departments: [], categories: [], students: [] }
    default:
      return state
  }
}
