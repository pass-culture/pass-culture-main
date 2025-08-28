import * as yup from 'yup'

declare module 'yup' {
  // Match Yup v1.x ArraySchema generic arity to avoid mismatches (omit constraints/defaults)
  /* biome-ignore lint/correctness/noUnusedVariables: module augmentation must mirror Yup's generic params */
  interface ArraySchema<TIn, TContext, TDefault, TFlags> {
    uniqueBy(key: string, message: string): this
  }
}

yup.addMethod(
  yup.array,
  'uniqueBy',
  function uniqueBy(key: string, message: string) {
    return this.test({
      name: 'unique-by',
      params: { key },
      message,
      test(value: unknown) {
        if (!Array.isArray(value)) {
          return true
        }

        const nonFalsyKeyValues = value
          .map<string | number>((item) => item[key])
          .filter(Boolean)

        // Performance shortcut
        const hasDuplicates =
          new Set(nonFalsyKeyValues).size !== nonFalsyKeyValues.length
        if (!hasDuplicates) {
          return true
        }

        const duplicateIndices: number[] = []
        const seenValues = new Set<string | number>()
        nonFalsyKeyValues.forEach((keyValue, index) => {
          if (seenValues.has(keyValue)) {
            duplicateIndices.push(index)
          } else {
            seenValues.add(keyValue)
          }
        })

        const validationErrors = duplicateIndices.map((duplicateIndex) =>
          this.createError({
            path: `${this.path}[${duplicateIndex}].${key}`,
            message,
          })
        )

        return new yup.ValidationError(validationErrors)
      },
    })
  }
)

export { yup }
