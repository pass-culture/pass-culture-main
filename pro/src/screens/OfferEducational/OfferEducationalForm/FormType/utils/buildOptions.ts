import { Category, SubCategory } from "custom_types/categories"

type Option = {
    value: string;
    label: string;
}

export const buildOptions = <T extends Category | SubCategory>(options: T[]): Option[] =>
  options.map(({ id, proLabel }) => ({ value: id, label: proLabel })) 
