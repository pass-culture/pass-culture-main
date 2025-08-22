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

        const checked = new Map<string | number, number[]>()

        for (let i = 0; i < value.length; i++) {
          const item = value[i]
          if (item == null) {
            continue
          }

          const prop = (item as Record<string, unknown>)[key]

          if (prop == null) {
            continue
          }

          const t = typeof prop
          if (t !== 'string' && t !== 'number') {
            continue
          }

          const comparable = prop as string | number
          const arr = checked.get(comparable)
          if (arr) {
            arr.push(i)
          } else {
            checked.set(comparable, [i])
          }
        }

        const duplicateIndices: number[] = []
        for (const indices of checked.values()) {
          if (indices.length > 1) {
            duplicateIndices.push(...indices)
          }
        }

        if (duplicateIndices.length > 0) {
          const errors = duplicateIndices.map((i) =>
            this.createError({ path: `${this.path}[${i}]`, message })
          )
          return new yup.ValidationError(errors)
        }

        return true
      },
    })
  }
)

export { yup }
