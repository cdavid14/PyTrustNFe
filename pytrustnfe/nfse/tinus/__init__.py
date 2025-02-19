# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Endereços Simpliss Piracicaba
# Homologação: http://wshomologacao.simplissweb.com.br/nfseservice.svc
# Homologação site: http://homologacaonovo.simplissweb.com.br/Account/Login

# Prod:http://sistemas.pmp.sp.gov.br/semfi/simpliss/contrib/Account/Login
# Prod:http://sistemas.pmp.sp.gov.br/semfi/simpliss/ws_nfse/nfseservice.svc

import os
from lxml import etree
from requests import Session
from zeep.transports import Transport
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from pytrustnfe.nfe.assinatura import Assinatura

from zeep import Client, Settings, xsd
from datetime import datetime, timedelta
import requests 

cidades = {
    "2402006": {
        "municipio": "Caicó",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testecai/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/caico/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2403103": {
        "municipio": "Currais Novos",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testecur/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/curraisnovos/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2403251": {
        "municipio": "Parnamirim",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testepar/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/parnamirim/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2408003": {
        "municipio": "Mossoró",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testemos/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/mossoro/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2412005": {
        "municipio": "São Goncalo",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testegon/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/saogoncalo/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2607901": {
        "municipio": "Jaboatão dos Guararapes",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testejab/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/jaboatao/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2609600": {
        "municipio": "Olinda",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testeoli/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/olinda/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2503209": {
        "municipio": "Cabedelo",
        "uf": "PB",
        "homologacao": "http://www2.tinus.com.br/csp/testecbd/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/cabedelo/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2603454": {
        "municipio": "Camaragibe",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testecam/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/camaragibe/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2407104": {
        "municipio": "Macaiba",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testemac/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/macaiba/WSNFSE",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2602902": {
        "municipio": "Cabo de Santo Agostinho",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testecab/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/cabo/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2606002": {
        "municipio": "Garanhuns",
        "uf": "PE",
        "homologacao": "http://www2.tinus.com.br/csp/testegar/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/garanhuns/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
    "2401453": {
        "municipio": "Barauna",
        "uf": "RN",
        "homologacao": "http://www2.tinus.com.br/csp/testebar/WSNFSE.",
        "producao": "http://www.tinus.com.br/csp/barauna/WSNFSE.",
        "version": "1.00",
        "msgns": "http://www2.tinus.com.br/WSNFSE"
    },
}

def _render_xml(certificado, method, **kwargs):
    kwargs['method'] = method
    if kwargs['ambiente'] == "homologacao":
        kwargs['soap_ns'] = "http://www2.tinus.com.br"
    else:
        kwargs['soap_ns'] = "http://www.tinus.com.br"
    path = os.path.join(os.path.dirname(__file__), "templates")
    parser = etree.XMLParser(
        remove_blank_text=True, remove_comments=True, strip_cdata=False
    )
    signer = Assinatura(certificado.pfx, certificado.password)

    referencia = ""
    xml_string_send = render_xml(path, "%s.xml" % method, True, **kwargs)

    # xml object
    xml_send = etree.fromstring(
        xml_string_send, parser=parser)

    if method == "RecepcionarLoteRps":
        referencia = kwargs.get("nfse").get("numero_lote")
        for item in kwargs["nfse"]["lista_rps"]:
            reference = "rps:{0}{1}".format(
                item.get('numero'), item.get('serie'))
            
            signer.assina_xml(xml_send, reference)

        xml_signed_send = signer.assina_xml(
            xml_send, "lote:{0}".format(referencia))
    else:
        xml_signed_send = etree.tostring(xml_send)

    return xml_signed_send

def _send(certificado, method, **kwargs):
    if method == "RecepcionarLoteRps":
        tinus = cidades[kwargs['nfse']['lista_rps'][0]['servico']['codigo_municipio']]
    else:
        tinus = cidades[kwargs['codigo_municipio']]
    if kwargs["ambiente"] == "producao":
        base_url = "%s%s.cls" %(tinus['producao'],method)
        soap_ns = "http://www.tinus.com.br"
    else:
        base_url = "%s%s.cls" %(tinus['homologacao'],method)
        soap_ns = "http://www2.tinus.com.br"

    xml_send = kwargs["xml"]
    path = os.path.join(os.path.dirname(__file__), "templates")
    soap = render_xml(path, "SoapRequest.xml", False, **{"soap_body":xml_send, "method": method, "soap_ns": soap_ns})

    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)
    session = Session()
    session.cert = (cert, key)
    session.verify = False
    action = "%s.%s.%s" %(tinus['msgns'],method,method)
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": action,
        "Content-length": str(len(soap))
    }

    request = requests.post(base_url, data=soap, headers=headers)
    response, obj = sanitize_response(request.content)
    return {"sent_xml": str(soap), "received_xml": str(response), "object": obj.Body }


def xml_recepcionar_lote_rps(certificado, **kwargs):
    return _render_xml(certificado, "RecepcionarLoteRps", **kwargs)


def recepcionar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    return _send(certificado,"RecepcionarLoteRps", **kwargs)


def xml_consultar_situacao_lote(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarSituacaoLoteRps", **kwargs)


def consultar_situacao_lote(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_situacao_lote(certificado, **kwargs)
    return _send(None, "ConsultarSituacaoLoteRps", **kwargs)


def consultar_nfse_por_rps(certificado, **kwargs):
    return _send(None, "ConsultarNfsePorRps", **kwargs)


def xml_consultar_lote_rps(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarLoteRps", **kwargs)


def consultar_lote_rps(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_consultar_lote_rps(certificado, **kwargs)
    return _send(certificado, "ConsultarLoteRps", **kwargs)


def xml_consultar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "ConsultarNfse", **kwargs)


def consultar_nfse(certificado, **kwargs):
    return _send("ConsultarNfse", **kwargs)


def xml_cancelar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "CancelarNfse", **kwargs)


def cancelar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_cancelar_nfse(certificado, **kwargs)
    return _send("CancelarNfse", **kwargs)


def xml_gerar_nfse(certificado, **kwargs):
    return _render_xml(certificado, "GerarNfse", **kwargs)


def gerar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_recepcionar_lote_rps(certificado, **kwargs)
    return _send("GerarNfse", **kwargs)
