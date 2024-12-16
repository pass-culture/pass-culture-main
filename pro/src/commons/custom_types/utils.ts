export type EnumType<T extends Record<string, any>> = T[keyof T]
