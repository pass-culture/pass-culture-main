import { DataProvider } from 'react-admin'

import { env } from '../libs/environment/env'
import { eventMonitoring } from '../libs/monitoring/sentry'
import {
  UserSearchResponse,
  UserApiResponse,
} from '../resources/Interfaces/UserSearchInterface'
import { UserManualReview } from '../resources/PublicUsers/types'

import { safeFetch } from './apiHelpers'

let assets: UserApiResponse[] = []

export const dataProvider: DataProvider = {
  async searchList(resource: string, params: string) {
    switch (resource) {
      case 'public_accounts/search': {
        const response = await safeFetch(
          `${env.API_URL}/${resource}?q=${encodeURIComponent(params)}`
        )

        const userSearchResponse: UserSearchResponse = response.json
        assets = userSearchResponse.accounts.map(item => ({
          ...item,
          id: item.id,
        }))

        assets = assets.filter(
          (obj, pos, arr) => arr.map(({ id }) => id).indexOf(obj.id) === pos
        )

        return {
          data: assets,
          total: assets.length,
        }
      }
      default:
        break
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getList(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  //@ts-ignore TODO: (akarki) reformatter le typage de la réponse
  async getOne(resource, params) {
    switch (resource) {
      case 'public_accounts': {
        try {
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
              return safeFetch(
                `${env.API_URL}/${resource}/${params.id}/history`
              )
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
        } catch (error) {
          eventMonitoring.captureException(error)
          throw error
        }
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

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore 12356
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async create(resource, params) {
    return {
      data: {
        id: 0,
      },
    }
  },
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore 12356
  async update(resource, params) {
    switch (resource) {
      case 'public_accounts': {
        try {
          const bodyString = JSON.stringify(params.data, null, 4)
          const body = {
            method: 'POST',
            body: bodyString,
            headers: new Headers({
              'Content-Type': 'application/json',
            }),
          }
          const response = await safeFetch(
            `${env.API_URL}/${resource}/${params.id}`,
            body
          )
          const responseData = await response.json()
          return {
            data: responseData,
          }
        } catch (error) {
          eventMonitoring.captureException(error)
          throw error
        }
      }
      default:
        break
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async updateMany(resource, params) {
    return {
      data: [],
    }
  },
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore 12356
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async delete(resource, params) {
    return {
      data: {
        id: 1,
      },
    }
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async deleteMany(resource, params) {
    return {
      data: [],
    }
  },
  async postUserManualReview(resource: string, params: UserManualReview) {
    try {
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

      console.log(requestParams)

      return await safeFetch(
        `${env.API_URL}/${resource}/${params.id}/review`,
        requestParams
      )
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
  async postResendValidationEmail(resource: string, params: UserApiResponse) {
    try {
      const requestParams = {
        method: 'POST',
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
      }
      return safeFetch(
        `${env.API_URL}/${resource}/${params.id}/resend-validation-email`,
        requestParams
      )
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
  async postSkipPhoneValidation(resource: string, params: UserApiResponse) {
    try {
      const requestParams = {
        method: 'POST',
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
      }
      return safeFetch(
        `${env.API_URL}/${resource}/${params.id}/skip-phone-validation`,
        requestParams
      )
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
  async postPhoneValidationCode(resource: string, params: UserApiResponse) {
    try {
      const requestParams = {
        method: 'POST',
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
      }
      return safeFetch(
        `${env.API_URL}/${resource}/${params.id}/send-phone-validation-code`,
        requestParams
      )
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
}
