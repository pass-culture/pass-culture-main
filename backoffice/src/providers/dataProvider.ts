import { CreateParams, DataProvider, GetListParams } from 'react-admin'

import { env } from '../libs/environment/env'
import { eventMonitoring } from '../libs/monitoring/sentry'
import {
  UserApiResponse,
  UserManualReview,
} from '../resources/PublicUsers/types'

import { safeFetch } from './apiHelpers'

export const dataProvider: DataProvider = {
  async searchList(resource: string, params: GetListParams) {
    let url = `${env.API_URL}/${resource}/search?q=${encodeURIComponent(
      params.meta.search
    )}&page=${params.pagination.page}&perPage=${params.pagination.perPage}`

    if (params.meta.type) {
      url += `&type=${params.meta.type}`
    }
    const response = await safeFetch(url)

    return {
      data: response.json.data,
      total: response.json.total,
      currentPage: response.json.page,
      totalPages: response.json.pages,
    }
  },

  //TODO: (akarki) - Implement ${params} when API is ready for it
  //
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getList(resource, params) {
    const response = await safeFetch(`${env.API_URL}/${resource}`)
    const rolesResponse = response.json
    let resourceResponse
    switch (resource) {
      case 'roles':
        resourceResponse = rolesResponse.roles
        break
      case 'permissions':
        resourceResponse = rolesResponse.permissions
        break
      default:
        break
    }
    return {
      data: resourceResponse,
      total: resourceResponse.length,
    }
  },

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  //@ts-ignore TODO: (akarki) - reformat ${response} when API is ready for it
  async getOne(resource, params) {
    switch (resource) {
      case 'public_accounts': {
        const response = await safeFetch(
          `${env.API_URL}/${resource}/${params.id}`
        )
        const user: UserApiResponse = response.json

        const creditInfo = async () => {
          try {
            return safeFetch(`${env.API_URL}/${resource}/${params.id}/credit`)
          } catch (error) {
            eventMonitoring.captureException(error)
            throw error
          }
        }

        const historyInfo = async () => {
          try {
            return safeFetch(`${env.API_URL}/${resource}/${params.id}/history`)
          } catch (error) {
            eventMonitoring.captureException(error)
            throw error
          }
        }

        const [userCreditResponse, userHistoryResponse] = await Promise.all([
          creditInfo(),
          historyInfo(),
        ])

        const dataUser = {
          ...user,
          userCredit: userCreditResponse.json,
          userHistory: userHistoryResponse.json,
        }
        return { data: dataUser }
      }
      default:
        break
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getMany(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getManyReference(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },

  async create(resource: string, params: CreateParams) {
    const requestParams = {
      method: 'POST',
      body: JSON.stringify(params.data),
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }

    const response = await safeFetch(
      `${env.API_URL}/${resource}`,
      requestParams
    )

    const responseData = await response.json

    return { data: responseData }
  },

  async update(resource, params) {
    const bodyString = JSON.stringify(params.data, null, 4)
    const body = {
      method: 'PUT',
      body: bodyString,
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    const response = await safeFetch(
      `${env.API_URL}/${resource}/${params.id}`,
      body
    )
    const responseData = response.json
    return {
      data: responseData,
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async updateMany(resource, params) {
    return {
      data: [],
    }
  },

  async delete(resource, params) {
    const requestParams = {
      method: 'DELETE',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    const response = await safeFetch(
      `${env.API_URL}/${resource}/${params.id}`,
      requestParams
    )
    const responseData = await response.json

    return { data: responseData }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async deleteMany(resource, params) {
    return {
      data: [],
    }
  },

  //TODO: (akarki) - To export to a dedicated file for custom operation on public_users
  async postUserManualReview(resource: string, params: UserManualReview) {
    const bodyString = JSON.stringify({
      eligibility: params.eligibility,
      reason: params.reason,
      review: params.review,
    })
    const requestParams = {
      method: 'POST',
      body: bodyString,
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    return await safeFetch(
      `${env.API_URL}/${resource}/${params.id}/review`,
      requestParams
    )
  },
  async postResendValidationEmail(resource: string, params: UserApiResponse) {
    const requestParams = {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    return await safeFetch(
      `${env.API_URL}/${resource}/${params.id}/resend-validation-email`,
      requestParams
    )
  },
  async postSkipPhoneValidation(resource: string, params: UserApiResponse) {
    const requestParams = {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    return await safeFetch(
      `${env.API_URL}/${resource}/${params.id}/skip-phone-validation`,
      requestParams
    )
  },
  async postPhoneValidationCode(resource: string, params: UserApiResponse) {
    const requestParams = {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
    return await safeFetch(
      `${env.API_URL}/${resource}/${params.id}/send-phone-validation-code`,
      requestParams
    )
  },
}
