import { Option } from 'app/types/option'

export type Filters = {
  departments: Option[]
  categories: Option<string[]>[]
  students: Option[]
  domains: Option<number>[]
  onlyInMySchool: boolean
}
