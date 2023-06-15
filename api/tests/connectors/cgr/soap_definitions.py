WEB_SERVICE_DEFINITION = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:s0="urn:GestionCinemaWS"
             xmlns="http://schemas.xmlsoap.org/wsdl/" targetNamespace="urn:GestionCinemaWS">
    <types>
        <xsd:schema elementFormDefault="unqualified" targetNamespace="urn:GestionCinemaWS">
            <xsd:complexType name="tGetSeancesPassCulture">
                <xsd:sequence>
                    <xsd:element name="User" type="xsd:string"/>
                    <xsd:element name="mdp" type="xsd:string"/>
                    <xsd:element name="IDFilmAllocine" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="GetSeancesPassCulture" type="s0:tGetSeancesPassCulture"/>
            <xsd:complexType name="tGetSeancesPassCultureResponse">
                <xsd:sequence>
                    <xsd:element name="GetSeancesPassCultureResult" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="GetSeancesPassCultureResponse" type="s0:tGetSeancesPassCultureResponse"/>
            <xsd:complexType name="tReservationPassCulture">
                <xsd:sequence>
                    <xsd:element name="User" type="xsd:string"/>
                    <xsd:element name="mdp" type="xsd:string"/>
                    <xsd:element name="pIDSeances" type="xsd:int"/>
                    <xsd:element name="pNumCinema" type="xsd:int"/>
                    <xsd:element name="pPUTTC" type="xsd:string"/>
                    <xsd:element name="pNBPlaces" type="xsd:int"/>
                    <xsd:element name="pNom" type="xsd:string"/>
                    <xsd:element name="pPrenom" type="xsd:string"/>
                    <xsd:element name="pEmail" type="xsd:string"/>
                    <xsd:element name="pToken" type="xsd:string"/>
                    <xsd:element name="pDateLimiteAnnul" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="ReservationPassCulture" type="s0:tReservationPassCulture"/>
            <xsd:complexType name="tReservationPassCultureResponse">
                <xsd:sequence>
                    <xsd:element name="ReservationPassCultureResult" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="ReservationPassCultureResponse" type="s0:tReservationPassCultureResponse"/>
            <xsd:complexType name="tAnnulationPassCulture">
                <xsd:sequence>
                    <xsd:element name="User" type="xsd:string"/>
                    <xsd:element name="mdp" type="xsd:string"/>
                    <xsd:element name="pQrCode" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="AnnulationPassCulture" type="s0:tAnnulationPassCulture"/>
            <xsd:complexType name="tAnnulationPassCultureResponse">
            <xsd:sequence>
                <xsd:element name="AnnulationPassCultureResult" type="xsd:string"/>
                </xsd:sequence>
                </xsd:complexType>
            <xsd:element name="AnnulationPassCultureResponse" type="s0:tAnnulationPassCultureResponse"/>
        </xsd:schema>
    </types>
    <message name="GestionCinemaWS_GetSeancesPassCulture_MessageIn">
        <part name="parameters" element="s0:GetSeancesPassCulture"/>
    </message>
    <message name="GestionCinemaWS_GetSeancesPassCulture_MessageOut">
        <part name="parameters" element="s0:GetSeancesPassCultureResponse"/>
    </message>
    <message name="GestionCinemaWS_ReservationPassCulture_MessageIn">
        <part name="parameters" element="s0:ReservationPassCulture"/>
    </message>
    <message name="GestionCinemaWS_ReservationPassCulture_MessageOut">
        <part name="parameters" element="s0:ReservationPassCultureResponse"/>
    </message>
    <message name="GestionCinemaWS_AnnulationPassCulture_MessageIn">
        <part name="parameters" element="s0:AnnulationPassCulture"/>
    </message>
    <message name="GestionCinemaWS_AnnulationPassCulture_MessageOut">
        <part name="parameters" element="s0:AnnulationPassCultureResponse"/>
    </message>
    <portType name="GestionCinemaWSSOAPPortType">
        <operation name="GetSeancesPassCulture">
            <input message="s0:GestionCinemaWS_GetSeancesPassCulture_MessageIn"/>
            <output message="s0:GestionCinemaWS_GetSeancesPassCulture_MessageOut"/>
        </operation>
        <operation name="ReservationPassCulture">
            <input message="s0:GestionCinemaWS_ReservationPassCulture_MessageIn"/>
            <output message="s0:GestionCinemaWS_ReservationPassCulture_MessageOut"/>
        </operation>
        <operation name="AnnulationPassCulture">
            <input message="s0:GestionCinemaWS_AnnulationPassCulture_MessageIn"/>
            <output message="s0:GestionCinemaWS_AnnulationPassCulture_MessageOut"/>
        </operation>
    </portType>
    <binding name="GestionCinemaWSSOAPBinding" type="s0:GestionCinemaWSSOAPPortType">
        <soap:binding transport="http://schemas.xmlsoap.org/soap/http" style="document"/>
        <operation name="GetSeancesPassCulture">
            <soap:operation soapAction="urn:GestionCinemaWS/GetSeancesPassCulture" style="document"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="ReservationPassCulture">
        <soap:operation soapAction="urn:GestionCinemaWS/ReservationPassCulture" style="document"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="AnnulationPassCulture">
            <soap:operation soapAction="urn:GestionCinemaWS/AnnulationPassCulture" style="document"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>
    <service name="GestionCinemaWS">
        <port name="GestionCinemaWSSOAPPort" binding="s0:GestionCinemaWSSOAPBinding">
            <soap:address location="http://192.168.1.1/GESTIONCINEMAWS_WEB/awws/GestionCinemaWS.awws"/>
        </port>
    </service>
</definitions>
"""
