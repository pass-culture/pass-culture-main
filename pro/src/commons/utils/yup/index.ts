import * as yup from 'yup'

/**
 * Extract the type of a collection item from a collection type,
 * or null | undefined if the collection type itself is null or undefined.
 */
type ItemType<T> =
  T extends Array<infer U>
    ? U
    : T extends null | undefined
      ? null | undefined
      : never

declare module 'yup' {
  // Match Yup v1.x ArraySchema generic arity to avoid mismatches (omit constraints/defaults)
  /* biome-ignore lint/correctness/noUnusedVariables: module augmentation must mirror Yup's generic params */
  interface ArraySchema<TIn, TContext, TDefault, TFlags> {
    /**
     * Ensure all items in the array are unique by a given key or computed key.
     *
     * @param key Key of the item to check uniqueness against,
     *            or, if `computeKey` is provided, `key` represents the name of the error path segment.
     * @param message Error message.
     * @param computeKey Compute a key value from the item to check uniqueness against.
     */
    uniqueBy(
      key: string,
      message: string,
      computeKey?: (item: ItemType<TIn>) => string | number | null | undefined
    ): this
  }
}

yup.addMethod(
  yup.array,
  'uniqueBy',
  function uniqueBy(
    key: string,
    message: string,
    computeKey?: (item: unknown) => string | number | null | undefined
  ) {
    return this.test({
      name: 'unique-by',
      params: { key },
      message,
      test(value: unknown) {
        if (!Array.isArray(value)) {
          return true
        }

        const keyValues = value.map((item) =>
          computeKey ? computeKey(item) : item?.[key]
        )
        const nonFalsyKeyValues = keyValues.filter(Boolean)

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
