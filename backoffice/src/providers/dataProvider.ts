import {DataProvider} from 'react-admin'
import {UserSearchInterface, UserApiInterface} from "../resources/Interfaces/UserSearchInterface";
import { env } from "../libs/environment/env";
import {UserCredit, UserManualReview} from "../resources/PublicUsers/types";


let assets: UserApiInterface[] = []
const urlBase = env.API_URL
export const dataProvider: DataProvider = {
    // @ts-ignore see later
    async searchList(resource: string, params: string) {
        switch (resource) {
            default:
            case 'public_users/search':
                // const response = await fetch(`https://backend.testing.passculture.team/backoffice/${resource}?q=`+ params)
                const token = localStorage.getItem('tokenApi')
                if (!token) {
                    return Promise.reject()
                }

                const body: object = {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
                const response = await fetch(`${env.API_URL}/${resource}?q=${encodeURIComponent(params)}`, body)
                const json: UserSearchInterface = await response.json()
                assets = json.accounts
                    .map((item) => ({
                        ...item,
                        id: item.id,
                    }))

                assets = assets
                    .filter((obj, pos, arr) => arr.map(({id}) => id).indexOf(obj.id) === pos)

                return {
                    data: assets,
                    total: assets.length,
                }

        }
    },
    // @ts-ignore see later
    async getList(resource, params) {

        if (resource.includes('/')) {
            switch (resource) {
                default:
                case 'public_users/search':
                    if (assets.length === 0) {
                        // @ts-ignore
                        const response = await fetch(`${urlBase}/${resource}/?q=${encodeURIComponent(params)}`)
                        const json: UserSearchInterface = await response.json()
                        assets = json.accounts
                            .map((item) => ({
                                ...item,
                                id: item.id,
                            }))

                        assets = assets
                            .filter((obj, pos, arr) => arr.map(({id}) => id).indexOf(obj.id) === pos)
                    }

                    return {
                        data: assets,
                        total: assets.length,
                    }
            }
        }
        return {
            data: [],
            total: 0,
        }
    },
    //@ts-ignore
    async getOne(resource, params) {
        switch (resource) {
            default:
                break;
            case 'public_accounts':
                const token = localStorage.getItem('tokenApi')
                if (!token) {
                    return Promise.reject()
                }

                try {
                    const body: object = {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    }
                    const response = await fetch(`${urlBase}/${resource}/${params.id}`, body)
                    const user: UserApiInterface = await response.json()

                    const creditInfo = async () => {
                        try {
                            return fetch(`${urlBase}/${resource}/${params.id}/credit`, body)
                        } catch (error) {
                            throw error
                        }
                    }

                    const historyInfo = async () => {
                        try {
                            return fetch(`${urlBase}/${resource}/${params.id}/history`, body)
                        } catch (error) {
                            throw error
                        }
                    }
                    const userCredit: UserCredit = await (await creditInfo()).json()
                    const userHistory = await (await historyInfo()).json()

                    const dataUser = {...user, userCredit, userHistory}
                    console.log(dataUser)
                    return {data: dataUser}
                } catch (error) {
                    throw error
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
    }
    ,
    // @ts-ignore
    async create(resource, params) {
        return {
            data: {
                id: 0,
            },
        }
    }
    ,
    // @ts-ignore
    async update(resource, params) {
        return {
            data: {},
        }
    }
    ,
    async updateMany(resource, params) {
        return {
            data: [],
        }
    }
    ,
    // @ts-ignore
    async delete(resource, params) {
        return {
            data: {
                id: 1,
            },
        }
    }
    ,
    async deleteMany(resource, params) {
        return {
            data: [],
        }
    }
    ,
    async postUserManualReview(resource: string, params: UserManualReview) {
        const token = localStorage.getItem('tokenApi')

        if (!token) {
            return Promise.reject()
        }
        try {
            const bodyString = JSON.stringify({
                "eligibility": params.eligibility,
                "reason": params.reason,
                "review": params.review
            })
            const requestParams: object = {
                method: 'POST',
                body: bodyString,
                headers: {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                }
            }

            console.log(requestParams)

            const response = await fetch(`${env.API_URL}/${resource}/${params.id}/review`, requestParams)

            return response
        } catch (error) {
            throw error
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
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
            const response = await fetch(`${env.API_URL}/${resource}/${params.id}/resend-validation-email`, requestParams)
            return response
        } catch (error) {
            throw error
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
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
            const response = await fetch(`${env.API_URL}/${resource}/${params.id}/skip-phone-validation`, requestParams)
            return response
        } catch (error) {
            throw error
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
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                }
            }
            const response = await fetch(`${env.API_URL}/${resource}/${params.id}/send-phone-validation-code`, requestParams)
            return response
        } catch (error) {
            throw error
        }
    },
}
