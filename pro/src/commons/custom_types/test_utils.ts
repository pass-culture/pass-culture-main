/**
 * Utility types for testing and type assertions.
 *
 * You can take advantage of `// @ts-expect-error` and `// @ts-expect-no-error` comments
 * to test your types in a TypeScript-friendly way.
 */

type StripNullishAndOptional<T> = {
  -readonly [K in keyof T]-?: NonNullable<T[K]>
}

/** Causes a compile error when `T` is not `true`. */
export type AssertTrue<T extends true> = T

/**
 * Assert that all properties of `Sub` exist in `Sup` with compatible *non-nullish* types.
 *
 * @description
 * - Enforces key presence: every key of `Sub` must exist in `Sup`.
 * - Compares value types after stripping `null | undefined` and optionality on both sides.
 *   (So `boolean` is considered compatible with `boolean | null | undefined`, etc.)
 *
 * @example
 * ```ts
 * interface CatOrDog {
 *   hasMeowFactor: boolean | null
 *   hasWoofFactor?: boolean | undefined
 * }
 * interface Cat {
 *   hasMeowFactor?: boolean
 * }
 * interface Dog {
 *   hasWoofFactor: boolean
 * }
 *
 * type _Success = AssertTrue<ThatSupTypePropsIncludeSubTypeProps<CatOrDog, Cat>>
 * // @ts-expect-error
 * type _Fail = AssertTrue<ThatSupTypePropsIncludeSubTypeProps<Dog, Cat>>
 * ```
 */
export type ThatSupTypePropsIncludeSubTypeProps<Sup, Sub> =
  // 1) Every key in Sub must exist in Sup
  keyof Sub extends keyof Sup
    ? // 2) Compare after removing null/undefined *and* optionality
      StripNullishAndOptional<
        Pick<Sub, keyof Sub>
      > extends StripNullishAndOptional<Pick<Sup, keyof Sub>>
      ? true
      : false
    : false
