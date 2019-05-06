const capitalize = (string = '') =>
  string ? `${string[0].toUpperCase()}${string.slice(1)}` : string

export default capitalize
