import { Filters, Option } from 'pages/AdageIframe/app/types'

type PopulateAllFiltersAction = {
  type: 'POPULATE_ALL_FILTERS'
  allFilters: {
    departments: Option[]
    categories: Option<string[]>[]
    students: Option[]
    domains: Option<number>[]
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

type PopulateDomainsFilterAction = {
  type: 'POPULATE_DOMAINS_FILTER'
  domainFilters: Option<number>[]
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

type RemoveDomainFilterAction = {
  type: 'REMOVE_ONE_DOMAIN_FILTER'
  domainFilter: Option<number>
}

type PopulateOnlyInMySchoolAction = {
  type: 'POPULATE_ONLY_IN_MY_SCHOOL'
  departmentFilter: Option<string>
}

type ResetOnlyInMySchoolAction = {
  type: 'RESET_ONLY_IN_MY_SCHOOL'
}

type PopulateOnlyInMyDptAction = {
  type: 'POPULATE_ONLY_IN_MY_DEPARTMENT'
  departmentFilter: Option<string>
}

type ResetOnlyInMyDptAction = {
  type: 'RESET_ONLY_IN_MY_DEPARTMENT'
}

export type FiltersReducerAction =
  | PopulateAllFiltersAction
  | ResetCurrentFiltersAction
  | PopulateDepartmentsFilterAction
  | PopulateCategoriesFilterAction
  | PopulateStudentsFilterAction
  | PopulateDomainsFilterAction
  | RemoveDepartmentFilterAction
  | RemoveCategoryFilterAction
  | RemoveStudentFilterAction
  | RemoveDomainFilterAction
  | PopulateOnlyInMySchoolAction
  | ResetOnlyInMySchoolAction
  | PopulateOnlyInMyDptAction
  | ResetOnlyInMyDptAction

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
        domains: action.allFilters.domains,
        onlyInMySchool: false,
        onlyInMyDpt: true,
      }
    case 'REMOVE_ONE_DEPARTMENT_FILTER': {
      const newDepartments = state.departments?.filter(
        department => department.value !== action.departmentFilter.value
      )
      return {
        ...state,
        departments: newDepartments,
        onlyInMySchool: false,
        onlyInMyDpt: false,
      }
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
    case 'REMOVE_ONE_DOMAIN_FILTER': {
      const newDomains = state.domains?.filter(
        domain => domain.value !== action.domainFilter.value
      )
      return { ...state, domains: newDomains }
    }
    case 'POPULATE_DEPARTMENTS_FILTER':
      return {
        ...state,
        departments: action.departmentFilters,
        onlyInMySchool: false,
        onlyInMyDpt: false,
      }
    case 'POPULATE_CATEGORIES_FILTER':
      return { ...state, categories: action.categoryFilters }
    case 'POPULATE_STUDENTS_FILTER':
      return { ...state, students: action.studentFilters }
    case 'POPULATE_DOMAINS_FILTER':
      return { ...state, domains: action.domainFilters }
    case 'RESET_CURRENT_FILTERS':
      return {
        departments: [],
        categories: [],
        students: [],
        domains: [],
        onlyInMySchool: false,
        onlyInMyDpt: false,
      }
    case 'POPULATE_ONLY_IN_MY_SCHOOL':
      return {
        ...state,
        departments: [action.departmentFilter],
        onlyInMySchool: true,
      }
    case 'RESET_ONLY_IN_MY_SCHOOL':
      return { ...state, onlyInMySchool: false }
    case 'POPULATE_ONLY_IN_MY_DEPARTMENT':
      return {
        ...state,
        departments: [action.departmentFilter],
        onlyInMyDpt: true,
      }
    case 'RESET_ONLY_IN_MY_DEPARTMENT':
      return {
        ...state,
        onlyInMyDpt: false,
      }
    default:
      return state
  }
}
