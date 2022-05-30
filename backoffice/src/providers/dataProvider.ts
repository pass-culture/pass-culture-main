import {DataProvider, GetListParams} from 'react-admin'
import {UserSearchInterface, UserApiInterface} from "../resources/Interfaces/UserSearchInterface";
import {stringify} from "querystring";

let assets: UserApiInterface[] = []
const urlBase = process.env.REACT_APP_URL_BASE
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
                        'Authorization': token,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
                const response = await fetch(`http://localhost/backoffice/${resource}?q=` + params, body)
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
                        const response = await fetch(`https://backend.testing.passculture.team/backoffice/public_accounts/search/?q=${params}`)
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
    // @ts-ignore
    async getOne(resource, params) {
        console.log(resource)
        switch (resource) {
            default:
                break;
            case 'public_accounts/user':
                const token = localStorage.getItem('tokenApi')
                if (!token) {
                    return Promise.reject()
                }

                const body: object = {
                    headers: {
                        'Authorization': token,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
                const response = await fetch(`http://localhost/backoffice/${resource}/` + params.id, body)
                const user: UserApiInterface = await response.json();
                console.log(user)
                return {data: user}
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
            data: {
                id: 1,
            },
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
}
