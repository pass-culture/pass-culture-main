import {Identifier, RaRecord} from "react-admin";

export interface UserApiInterface extends RaRecord{
    id : Identifier,
    firstName: string,
    lastName: string,
    dateOfBirth: string,
    email: string,
    phoneNumber: string
}
export interface UserSearchInterface {
    accounts : UserApiInterface[]
}