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
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="GetSeancesPassCulture" type="s0:tGetSeancesPassCulture"/>
            <xsd:complexType name="tGetSeancesPassCultureResponse">
                <xsd:sequence>
                    <xsd:element name="GetSeancesPassCultureResult" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="GetSeancesPassCultureResponse" type="s0:tGetSeancesPassCultureResponse"/>
        </xsd:schema>
    </types>
    <message name="GestionCinemaWS_GetSeancesPassCulture_MessageIn">
        <part name="parameters" element="s0:GetSeancesPassCulture"/>
    </message>
    <message name="GestionCinemaWS_GetSeancesPassCulture_MessageOut">
        <part name="parameters" element="s0:GetSeancesPassCultureResponse"/>
    </message>
    <portType name="GestionCinemaWSSOAPPortType">
        <operation name="GetSeancesPassCulture">
            <input message="s0:GestionCinemaWS_GetSeancesPassCulture_MessageIn"/>
            <output message="s0:GestionCinemaWS_GetSeancesPassCulture_MessageOut"/>
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
    </binding>
    <service name="GestionCinemaWS">
        <port name="GestionCinemaWSSOAPPort" binding="s0:GestionCinemaWSSOAPBinding">
            <soap:address location="http://192.168.1.1/GESTIONCINEMAWS_WEB/awws/GestionCinemaWS.awws"/>
        </port>
    </service>
</definitions>
"""
