import type { APIRequestContext } from '@playwright/test'

export const BASE_API_URL = 'http://localhost:5001'

const SANDBOX_TIMEOUT = 120000

export async function sandboxCall<T = unknown>(
  request: APIRequestContext,
  method: 'GET' | 'POST',
  url: string
): Promise<T> {
  const response = await request.fetch(url, {
    method,
    timeout: SANDBOX_TIMEOUT,
    failOnStatusCode: false,
  })

  if (response.status() === 200) {
    return response.json() as Promise<T>
  }

  const body = await response.text()
  throw new Error(
    `Sandbox call failed: ${response.status()} - ${response.statusText()} - ${body}`
  )
}

export interface ProUserData {
  user: {
    email: string
  }
}

export interface ProUserWithActiveCollectiveOfferResponse {
  user: {
    email: string
  }
  offer: {
    id: number
    name: string
    venueName: string
  }
  stock: {
    startDatetime: string
  }
  providerApiKey: string
}

export interface DeskBookingsData {
  user: {
    email: string
  }
  tokenConfirmed: string
  tokenTooSoon: string
  tokenUsed: string
  tokenCanceled: string
  tokenReimbursed: string
  tokenOther: string
}

export async function createProUserWithBookings(
  request: APIRequestContext
): Promise<DeskBookingsData> {
  return await sandboxCall<DeskBookingsData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_bookings`
  )
}

export async function createRegularProUser(
  request: APIRequestContext
): Promise<ProUserData> {
  return await sandboxCall<ProUserData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_regular_pro_user_already_onboarded`
  )
}

export async function createNewProUser(
  request: APIRequestContext
): Promise<ProUserData> {
  return await sandboxCall<ProUserData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_new_pro_user`
  )
}

export async function createProUserWithActiveCollectiveOffer(
  request: APIRequestContext
): Promise<ProUserWithActiveCollectiveOfferResponse> {
  return await sandboxCall<ProUserWithActiveCollectiveOfferResponse>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_active_collective_offer`
  )
}

export async function createProUserWithVirtualOffer(
  request: APIRequestContext
): Promise<ProUserData> {
  return await sandboxCall<ProUserData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_regular_pro_user_with_virtual_offer`
  )
}

export interface ProUserWithOffererData {
  user: {
    email: string
  }
  siren: string
}

export interface ProUserWithOffererAndVenueData {
  user: {
    email: string
  }
  siret: string
}

export async function createNewProUserAndOfferer(
  request: APIRequestContext
): Promise<ProUserWithOffererData> {
  return await sandboxCall<ProUserWithOffererData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_new_pro_user_and_offerer`
  )
}

export async function createNewProUserAndOffererWithVenue(
  request: APIRequestContext
): Promise<ProUserWithOffererAndVenueData> {
  return await sandboxCall<ProUserWithOffererAndVenueData>(
    request,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_new_pro_user_and_offerer_with_venue`
  )
}
