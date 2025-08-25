import type { FieldValues, Path, UseFormReturn } from 'react-hook-form'

export function hasFormChanged<T extends FieldValues>({
  form,
  fields,
  initialValues,
}: {
  // biome-ignore lint/suspicious/noExplicitAny: This is a `react-hook-form` generic type.
  form: UseFormReturn<T, any, FieldValues>
  fields: Array<keyof T>
  initialValues: T
}): boolean {
  return fields.some((field) => {
    const fieldState = form.getFieldState(field as Path<T>)
    const fieldValue = form.getValues(field as Path<T>)

    return fieldState.isTouched && fieldValue !== initialValues[field]
  })
}
