/**
 * Makes all properties of T optional, recursively.
 * Useful for creating partial test data or mocks with deeply nested objects.
 *
 * @template T - The type to make deeply partial
 * @example
 * type Foo = { a: number; b: { c: string } }
 * type PartialFoo = DeepPartial<Foo>
 * // PartialFoo is { a?: number; b?: { c?: string } }
 */

export type DeepPartial<T> = T extends object
  ? {
      [P in keyof T]?: DeepPartial<T[P]>
    }
  : T
