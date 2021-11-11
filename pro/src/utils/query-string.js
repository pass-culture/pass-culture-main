export const parse = queryParams => Object.fromEntries(new URLSearchParams(queryParams))

export const stringify = queryParams => new URLSearchParams(queryParams).toString()
