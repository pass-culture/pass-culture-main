export function formatPrice(price: number, options?: Intl.NumberFormatOptions) {
  return Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    ...options,
  }).format(price)
}
