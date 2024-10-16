export const getLabelString = (label: string | JSX.Element): string =>
  typeof label === 'string' ? label : ''
