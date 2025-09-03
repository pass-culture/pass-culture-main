import { CurrencyEnum } from '@/commons/core/shared/types'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'

import { formatPrice } from './formatPrice'

type CurrencyOptions = { from: CurrencyEnum; to: CurrencyEnum }

export function formatPriceByCurrency(
  price: number,
  deviseOptions: CurrencyOptions,
  options?: Intl.NumberFormatOptions
): string {
  if (deviseOptions.from === CurrencyEnum.EUR) {
    switch (deviseOptions.to) {
      case CurrencyEnum.EUR:
        return formatPrice(price, options)
      case CurrencyEnum.XPF: {
        const priceInXpf = convertEuroToPacificFranc(price)
        return formatPacificFranc(priceInXpf, options)
      }
    }
  }
  throw new Error(
    `Conversion from ${deviseOptions.from} to ${deviseOptions.to} is not supported.`
  )
}
