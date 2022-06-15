import { DataProvider, GetOneResult } from 'react-admin'
import {
  UserSearchInterface,
  UserApiInterface,
} from '../resources/Interfaces/UserSearchInterface'
import { env } from '../libs/environment/env'
import { UserCredit, UserManualReview } from '../resources/PublicUsers/types'
import { captureException } from '@sentry/react'

let assets: UserApiInterface[] = []
const urlBase = env.API_URL
export const dataProvider: DataProvider = {
  async searchList(resource: string, params: string) {
    switch (resource) {
      default:
      case 'public_users/search':
        const token = localStorage.getItem('tokenApi')
        if (!token) {
          return Promise.reject()
        }

        const body: object = {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
        const response = await fetch(
          `${env.API_URL}/${resource}?q=${encodeURIComponent(params)}`,
          body
        )
        const json: UserSearchInterface = await response.json()
        assets = json.accounts.map(item => ({
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
  },
  async getList(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },
  //@ts-ignore TODO: (akarki) refortmatter le typage de la réponse
  async getOne(resource, params) {
    switch (resource) {
      default:
        break
      case 'public_accounts':
        const token = localStorage.getItem('tokenApi')
        if (!token) {
          return Promise.reject()
        }

        try {
          const body: object = {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/x-www-form-urlencoded',
            },
          }
          const response = await fetch(
            `${urlBase}/${resource}/${params.id}`,
            body
          )
          const user: UserApiInterface = await response.json()

          const creditInfo = async () => {
            try {
              return fetch(`${urlBase}/${resource}/${params.id}/credit`, body)
            } catch (error) {
              captureException(error)
            }
          }

          const historyInfo = async () => {
            try {
              return fetch(`${urlBase}/${resource}/${params.id}/history`, body)
            } catch (error) {
              captureException(error)
            }
          }
          const [userCredit, userHistory] = await Promise.all([
            creditInfo(),
            historyInfo(),
          ])

          const dataUser = { ...user, userCredit, userHistory }
          return { data: dataUser }
        } catch (error) {
          captureException(error)
        }
    }
  },
  async getMany(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },
  async getManyReference(resource, params) {
    return {
      data: [],
      total: 0,
    }
  },
  // @ts-ignore
  async create(resource, params) {
    return {
      data: {
        id: 0,
      },
    }
  },
  // @ts-ignore
  async update(resource, params) {
    switch (resource) {
      default:
        break
      case 'public_accounts':
        const token = localStorage.getItem('tokenApi')
        if (!token) {
          return Promise.reject()
        }

        try {
          const bodyString = JSON.stringify(params.data, null, 4)
          const body: object = {
            method: 'POST',
            body: bodyString,
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
          const response = await fetch(
            `${env.API_URL}/${resource}/${params.id}`,
            body
          )
          const responseData = await response.json()
          return {
            data: responseData,
          }
        } catch (error) {
          captureException(error)
        }
    }
  },
  async updateMany(resource, params) {
    return {
      data: [],
    }
  },
  // @ts-ignore
  async delete(resource, params) {
    return {
      data: {
        id: 1,
      },
    }
  },
  async deleteMany(resource, params) {
    return {
      data: [],
    }
  },
  async postUserManualReview(resource: string, params: UserManualReview) {
    const token = localStorage.getItem('tokenApi')

    if (!token) {
      return Promise.reject()
    }
    try {
      const bodyString = JSON.stringify({
        eligibility: params.eligibility,
        reason: params.reason,
        review: params.review,
      })
      const requestParams: object = {
        method: 'POST',
        body: bodyString,
        headers: {
          Authorization: 'Bearer ' + token,
          'Content-Type': 'application/json',
        },
      }

      console.log(requestParams)

      const response = await fetch(
        `${env.API_URL}/${resource}/${params.id}/review`,
        requestParams
      )

      return response
    } catch (error) {
      captureException(error)
    }
  },
  async postResendValidationEmail(resource: string, params: UserApiInterface) {
    const token = localStorage.getItem('tokenApi')
    if (!token) {
      return Promise.reject()
    }
    try {
      const requestParams: object = {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
      const response = await fetch(
        `${env.API_URL}/${resource}/${params.id}/resend-validation-email`,
        requestParams
      )
      return response
    } catch (error) {
      captureException(error)
    }
  },
  async postSkipPhoneValidation(resource: string, params: UserApiInterface) {
    const token = localStorage.getItem('tokenApi')
    if (!token) {
      throw new Error()
    }
    try {
      const requestParams: object = {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
      const response = await fetch(
        `${env.API_URL}/${resource}/${params.id}/skip-phone-validation`,
        requestParams
      )
      return response
    } catch (error) {
      captureException(error)
    }
  },
  async postPhoneValidationCode(resource: string, params: UserApiInterface) {
    const token = localStorage.getItem('tokenApi')
    if (!token) {
      throw new Error()
    }
    try {
      const requestParams: object = {
        method: 'POST',
        headers: {
          Authorization: 'Bearer ' + token,
          'Content-Type': 'application/json',
        },
      }
      const response = await fetch(
        `${env.API_URL}/${resource}/${params.id}/send-phone-validation-code`,
        requestParams
      )
      return response
    } catch (error) {
      captureException(error)
    }
  },
}
