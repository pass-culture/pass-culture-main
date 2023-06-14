/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingFormula } from './BookingFormula';
import type { BookingOfferType } from './BookingOfferType';

export type GetBookingResponse = {
  bookingId: string;
  dateOfBirth?: string | null;
  datetime: string;
  ean13?: string | null;
  email: string;
  /**
   * S'applique uniquement aux offres de catégorie Cinéma. Abonnement (ABO) ou place (PLACE).
   */
  formula?: BookingFormula | null;
  isUsed: boolean;
  offerId: number;
  offerName: string;
  offerType: BookingOfferType;
  phoneNumber?: string | null;
  price: number;
  priceCategoryLabel?: string | null;
  publicOfferId: string;
  quantity: number;
  /**
   * Identifiant du film et de la salle dans le cas d’une offre synchronisée par Allociné.
   */
  theater: Record<string, any>;
  userName: string;
  venueAddress?: string | null;
  venueDepartmentCode?: string | null;
  venueName: string;
};

