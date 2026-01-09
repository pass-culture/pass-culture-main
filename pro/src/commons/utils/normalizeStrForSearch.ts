export const normalizeStrForSearch = (str: string): string => {
  return (
    str
      .trim()
      .toLowerCase()
      // Expand ligatures (NFD doesn't decompose them)
      .replace(/œ/g, 'oe')
      .replace(/æ/g, 'ae')
      // Normalize to NFD (Normalization Form Canonical Decomposition), i.e.: "è" becomes "e ̀"
      .normalize('NFD')
      // Remove non-alphanumeric characters (including decomposed accents)
      .replace(/[^a-z0-9-\s]/g, '')
      // Deduplicate spaces
      .replace(/\s+/g, ' ')
  )
}
